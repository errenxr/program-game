import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from hardware.rfid_reader import RFIDReader
from hardware.rfid_map import RFID_MAP
from hardware.led_controller import LEDController
import tkinter as tk
from game.game_manager import GameManager
from PIL import Image, ImageTk
from game.api_client import get_active_anak, start_session, end_session
from ai.agent import Agent
from ai.environment import get_state, get_reward, apply_action
from game.api_client import update_level, get_current_user

IMAGES = ["airplane", "ant", "apple", "bicycle", "blueberry", "broccoli", "bulldozer",
          "capung", "car", "cat", "clownfish", "dog", "dolphin", "duck",
          "fish", "frog", "gurita", "heli", "koala", "lion", "monkey", "mushroom",
          "penyu", "pilot", "rabbit", "rhinoceros", "sheep", "siput", "sun", "terong",
          "tiger", "tomato", "train", "watermelon"]

COLORS = ["red", "blue", "pink", "green", "yellow", "darkpurple", "orange", "peach", "darkgrey", "lightblue", "wine", "navy"]

# Palette warna
BG          = "#FFF8F0"
HEADER_BG   = "#FF9DC6"
ACCENT1     = "#FF6B9D"
ACCENT2     = "#FFD166"
CORRECT     = "#77DD77"
WRONG       = "#FF6B6B"
BTN_NORMAL  = "#FFFFFF"
BTN_HOVER   = "#FFF0F8"
TITLE_FG    = "#4A2060"
TIMER_OK    = "#2ECC71"
TIMER_WARN  = "#F39C12"
TIMER_CRIT  = "#E74C3C"
SCORE_FG    = "#FF6B9D"
BUBBLE1     = "#FFD6E8"
BUBBLE2     = "#D6EEFF"
BUBBLE3     = "#D6FFE4"


def make_rounded_rect(canvas, x1, y1, x2, y2, r=20, **kwargs):
    pts = [
        x1+r, y1, x2-r, y1,
        x2, y1, x2, y1+r,
        x2, y2-r, x2, y2,
        x2-r, y2, x1+r, y2,
        x1, y2, x1, y2-r,
        x1, y1+r, x1, y1,
        x1+r, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kwargs)


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None,
                 width=180, height=48, r=24,
                 bg_color=ACCENT1, fg_color="#ffffff",
                 hover_color="#E0558A", font_spec=("Nunito", 14, "bold"),
                 **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=parent["bg"], highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color

        # Shadow (FIX)
        make_rounded_rect(self, 4, 4, width-1, height-1, r,
                          fill="#D3D3D3", outline="")

        self._rect = make_rounded_rect(self, 0, 0, width-4, height-4, r,
                                       fill=bg_color, outline="")
        self._text = self.create_text(width//2 - 2, height//2 - 2,
                                      text=text, fill=fg_color,
                                      font=font_spec)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _on_enter(self, _):
        self.itemconfig(self._rect, fill=self.hover_color)
        self.configure(cursor="hand2")

    def _on_leave(self, _):
        self.itemconfig(self._rect, fill=self.bg_color)
        self.configure(cursor="")

    def _on_click(self, _):
        if self.command:
            self.command()


class GameScreen:
    def __init__(self, root, mode="picture", user=None):
        self.root = root
        self.root.geometry("1024x600")
        self.root.resizable(False, False)
        self.rfid_reader = RFIDReader()
        self.led = LEDController()

        self.mode = mode
        user_id = get_current_user()
        print("USER_ID dari web:", user_id)
        
        if user_id:
            self.user = get_active_anak(user_id)
        else:
            self.user = None
            
        if not self.user:
            print("Tidak ada anak aktif dari web!")
        else:
            print("Anak aktif:", self.user["nama_anak"])
        
        if self.user:
            self.session_id = start_session(self.user["id"])
            self.agent = Agent(self.user["id"])
            print("Session ID:", self.session_id)
        else:
            self.agent = None
            self.session_id = None

        self.items = IMAGES if mode == "picture" else COLORS

        self.root.configure(bg=BG)

        # Background
        self.canvas_bg = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.canvas_bg.place(relwidth=1, relheight=1)

        self.canvas_bg.create_oval(-100, 380, 260, 740, fill=BUBBLE1, outline="")
        self.canvas_bg.create_oval(780, -120, 1140, 240, fill=BUBBLE2, outline="")
        self.canvas_bg.create_oval(450, 520, 570, 640, fill=BUBBLE3, outline="")

        # FIX warna transparansi
        self.canvas_bg.create_oval(60, 60, 130, 130, fill="#FFE7A0", outline="")
        self.canvas_bg.create_oval(880, 520, 940, 580, fill="#FF9FC0", outline="")

        self.canvas_bg.lower("all")

        self.is_locked = False
        self.button_map = {}
        self.game_active = True

        if self.user and "umur" in self.user:
            age = int(self.user["umur"])
        else:
            print("Umur user tidak tersedia, default ke 7 tahun")
            age = 7

        if self.user and "current_level" in self.user:
            level = self.user["current_level"]
        else:
            level = "mudah"

        self.game = GameManager(self.items, age=age, level=level, max_time=20*60)
        self.question = self.game.start_game()

        # Header
        self.frame_header = tk.Frame(self.root, bg=HEADER_BG)
        self.frame_header.pack(fill="x")

        title_text = "✨ Pilih satu gambar ✨" if self.mode == "picture" else "Pilih satu warna"

        self.title_label = tk.Label(
            self.frame_header,
            text=title_text,
            font=("Nunito", 16, "bold"),
            fg="#ffffff",
            bg=HEADER_BG,
            pady=4
        )
        self.title_label.pack(side="left", padx=20)

        self.stop_button = RoundedButton(
             self.frame_header,
             text="Berhenti",
             command=self.stop_game,
             width=140,
             height=40,
             bg_color="#E74C3C",
             hover_color="#C0392B"
             )
        self.stop_button.pack(side="left", padx=10)

        self.frame_info = tk.Frame(self.frame_header, bg=HEADER_BG)
        self.frame_info.pack(side="right", padx=20, pady=6)
        self.session_ended = False

        self.timer_canvas = tk.Canvas(self.frame_info, width=180, height=38,
                                      bg=HEADER_BG, highlightthickness=0)
        self.timer_canvas.pack(side="top")

        self._timer_rect = make_rounded_rect(self.timer_canvas, 0, 0, 178, 36, r=18,
                                             fill=TIMER_OK, outline="")

        self._timer_text_id = self.timer_canvas.create_text(
            89, 18, text="⏱  60 detik", fill="#ffffff",
            font=("Nunito", 13, "bold")
        )

        self.progress_label = tk.Label(
            self.frame_info,
            text="",
            font=("Nunito", 11, "bold"),
            fg="#ffffff",
            bg=HEADER_BG
        )
        self.progress_label.pack(side="top", pady=(2, 0))

        self.frame_game = tk.Frame(self.root, bg=BG)
        self.frame_game.pack(expand=True, pady=6)

        # Load gambar
        self.image_objects = {}
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

        for name in self.items:
            try:
                path = os.path.join(BASE_DIR, "assets", "images", f"{name}.png")
                image = Image.open(path).convert("RGBA")
                image = image.resize((120, 120))
                self.image_objects[name] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Gagal load gambar: {name} -> {e}")

        self.buttons = []
        self.render_question()
        self.update_timer()
        self.check_rfid()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.rfid_reader.cleanup()
        self.led.cleanup()
        self.root.destroy()
    
    def check_rfid(self):
        if not self.game_active:
            return
        
        uid = self.rfid_reader.read_uid()
        if uid:
            uid = uid.strip().upper()
            print("UID terbaca:", uid)
            
            if uid in RFID_MAP:
                item = RFID_MAP[uid]
                print("Item hasil mapping:", item)
                
                if item in self.question:
                    self.handle_click(item)
                
                else:
                    print("Item tidak ada di soal sekarang")
            
            else:
                print("Kartu tidak terdaftar!")
        
        else:
            print("UID terbaca: None")
        
        self.root.after(200, self.check_rfid)  

    def update_timer(self):
        if not self.game_active:
            return

        remaining = self.game.get_remaining_time()

        if remaining > 20:
            color = TIMER_OK
        elif remaining > 10:
            color = TIMER_WARN
        else:
            color = TIMER_CRIT

        self.timer_canvas.itemconfig(self._timer_rect, fill=color)

        minutes = remaining // 60
        seconds = remaining % 60
        self.timer_canvas.itemconfig(
            self._timer_text_id,
            text=f"⏱  {minutes:02}:{seconds:02}"
        )

        if remaining > 0:
            self.root.after(1000, self.update_timer)
        else:
            score = self.game.scoring.get_score()
            self.show_result(score)

    def render_question(self):
        for btn in self.buttons:
            btn.destroy()

        self.buttons.clear()
        self.button_map.clear()

        cols = 4

        self.progress_label.config(
            text=f" {len(self.game.current_selected_items)} / {len(self.game.base_images)}"
        )

        for index, item in enumerate(self.question):
            row = index // cols
            col = index % cols

            img = self.image_objects.get(item)

            card = tk.Canvas(self.frame_game, width=148, height=148,
                             bg=BG, highlightthickness=0)

            # FIX shadow
            make_rounded_rect(card, 4, 4, 147, 147, r=18,
                              fill="#D3D3D3", outline="")

            rect_id = make_rounded_rect(card, 0, 0, 143, 143, r=18,
                                        fill=BTN_NORMAL, outline="#E8D5F0", width=2)

            img_id = card.create_image(71, 71, image=img)
            card.image = img
            card._rect_id = rect_id

            card.bind("<Button-1>", lambda e, i=item: self.handle_click(i))
            card.grid(row=row, column=col, padx=14, pady=14)

            self.buttons.append(card)
            self.button_map[item] = card

    def handle_click(self, item):
        if self.is_locked:
            return

        result = self.game.select_item(item)
        print("RESULT:", result)

        if result:
            print("LED HIJAU NYALA")
            self.led.green_on()
        else:
            print("LED MERAH NYALA")
            self.led.red_on()

        card = self.button_map.get(item)

        if card:
            color = CORRECT if result else WRONG
            card.itemconfig(card._rect_id, fill=color)

        if self.game.is_episode_finished():
            print("Episode selesai → AI jalan")
            self.process_ai_episode()

        if self.game.is_game_over():
            score = self.game.scoring.get_score()
            self.show_result(score)
            return

        self.is_locked = True
        self.root.after(500, self.next_question)

    def next_question(self):
        if not self.game_active:
            return
        self.is_locked = False
        self.question = self.game.current_question
        self.render_question()

    def show_result(self, score):
        if self.session_id and not self.session_ended:
            end_session(self.session_id, score, self.game.level)
            if self.user:
                print("Update level ke database:", self.game.level)

            self.session_ended = True
            print("Session ended with score:", score)
            
        self.game_active = False

        self.frame_header.destroy()
        self.frame_game.destroy()

        frame = tk.Frame(self.root, bg=BG)
        frame.place(relwidth=1, relheight=1)

        card_canvas = tk.Canvas(frame, width=420, height=300,
                                bg=BG, highlightthickness=0)
        card_canvas.place(relx=0.5, rely=0.5, anchor="center")

        # FIX shadow
        make_rounded_rect(card_canvas, 5, 5, 419, 299, r=30,
                          fill="#D3D3D3", outline="")

        make_rounded_rect(card_canvas, 0, 0, 414, 294, r=30,
                          fill="#ffffff", outline=ACCENT1, width=2)

        card_canvas.create_text(207, 50, text="Hore, Selesai!",
                                font=("Nunito", 18, "bold"), fill=TITLE_FG)

        card_canvas.create_text(207, 175, text=str(score),
                                font=("Nunito", 72, "bold"), fill=SCORE_FG)

        btn = RoundedButton(
            frame,
            text="Kembali ke Menu",
            command=self.back_to_menu,
            width=220, height=50
        )
        btn.place(relx=0.5, rely=0.83, anchor="center")

    def back_to_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        from ui.screens.menu_screen import MenuScreen
        MenuScreen(self.root)

    def run(self):
        self.root.mainloop()
    
    def stop_game(self):
        if not self.game_active:
            return
        print("Game dihentikan oleh orang tua")
        
        self.game_active = False
        score = self.game.scoring.get_score()
        
        if self.session_id and not self.session_ended:
            end_session(self.session_id, score, self.game.level)
            self.session_ended = True
            print("Session dihentikan manual. Score:", score)
            
        self.show_result(score)
    
    def process_ai_episode(self):
        if not self.agent:
            return
        
        #performa
        persentase = self.game.get_episode_performance()
        level = self.game.level
        
        print("Performa:", persentase, "Level:", level)
        
        #state
        state = get_state(level, persentase)
        
        #pilih action
        action = self.agent.choose_action(state)
        
        # reward
        reward = get_reward(persentase, level, action)
        
        #next level
        new_level = apply_action(level, action)
        print(f"[LEVEL UPDATE] {level} → {new_level}")
        
        #next state
        next_state = get_state(new_level, persentase)
        
        #update Q-table
        self.agent.learn(state, action, reward, next_state)
        print(f"[AI] State: {state} → Action: {action} → Level baru: {new_level}")
        
        # reset episode
        self.game.reset_episode(new_level)
