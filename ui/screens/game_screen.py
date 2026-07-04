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
from logger.activity_logger import ActivityLogger

IMAGES = ["airplane", "ant", "apple", "bicycle", "blueberry", "broccoli", "bulldozer",
          "capung", "car", "cat", "clownfish", "dog", "dolphin", "duck",
          "fish", "frog", "gurita", "heli", "koala", "lion", "lobak", "monkey", "mushroom",
          "penyu", "pilot", "pinguin", "rabbit", "rhinoceros", "sheep", "siput", "sun", "terong",
          "tiger", "tomato", "train", "watermelon"]

COLORS = ["red", "blue", "pink", "green", "yellow", "darkpurple", "orange", "peach",
          "darkgrey", "lightblue", "wine", "navy"]

# ── Palette warna ──────────────────────────────────────────────
BG          = "#FFF8F0"
HEADER_BG   = "#88C9FF"     
ACCENT1     = "#FF6B9D"
ACCENT2     = "#FFD166"
CORRECT     = "#5EC97A"
WRONG       = "#F06B6B"
BTN_NORMAL  = "#FFFFFF"
BTN_BORDER  = "#D6E4FF"
TITLE_FG    = "#FFFFFF"
TIMER_OK    = "#3CB371"
TIMER_WARN  = "#E8A020"
TIMER_CRIT  = "#D94040"
SCORE_FG    = "#5B8DEF"
BUBBLE1     = "#DCE8FF"
BUBBLE2     = "#FFD6E8"
BUBBLE3     = "#D6FFE4"
QUESTION_BG = "#FFFFFF"
QUESTION_FG = "#5B8DEF"
PROGRESS_OK = "#5EC97A"
SHADOW      = "#C8C8C8"
# ───────────────────────────────────────────────────────────────


def make_rounded_rect(canvas, x1, y1, x2, y2, r=20, **kwargs):
    pts = [
        x1+r, y1,  x2-r, y1,
        x2,   y1,  x2,   y1+r,
        x2,   y2-r, x2,  y2,
        x2-r, y2,  x1+r, y2,
        x1,   y2,  x1,   y2-r,
        x1,   y1+r, x1,  y1,
        x1+r, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kwargs)


class RoundedButton(tk.Canvas):
    """Tombol bergaya dengan sudut membulat."""

    def __init__(self, parent, text, command=None,
                 width=180, height=48, r=24,
                 bg_color=ACCENT1, fg_color="#ffffff",
                 hover_color="#E0558A", font_spec=("Helvetica", 13, "bold"),
                 **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=parent["bg"], highlightthickness=0, **kwargs)
        self.command    = command
        self.bg_color   = bg_color
        self.hover_color = hover_color
        self.fg_color   = fg_color

        make_rounded_rect(self, 4, 4, width-1, height-1, r, fill=SHADOW, outline="")
        self._rect = make_rounded_rect(self, 0, 0, width-4, height-4, r,
                                       fill=bg_color, outline="")
        self._text = self.create_text(width//2 - 2, height//2 - 2,
                                      text=text, fill=fg_color, font=font_spec)

        self.bind("<Enter>",    self._on_enter)
        self.bind("<Leave>",    self._on_leave)
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
            self.logger = ActivityLogger(
                session_id=self.session_id,
                anak_id=self.user["id"]
            )
            print("Session ID:", self.session_id)
        else:
            self.agent = None
            self.session_id = None

        self.items = IMAGES if mode == "picture" else COLORS
        self.root.configure(bg=BG)

        # ── Dekorasi latar ──────────────────────────────────────
        self.canvas_bg = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.canvas_bg.place(relwidth=1, relheight=1)
        self.canvas_bg.create_oval(-100, 380, 260, 740, fill=BUBBLE1, outline="")
        self.canvas_bg.create_oval(780, -120, 1140, 240, fill=BUBBLE2, outline="")
        self.canvas_bg.create_oval(450, 500, 580, 630, fill=BUBBLE3, outline="")
        self.canvas_bg.create_oval(55,  55,  125, 125, fill="#FFE7A0", outline="")
        self.canvas_bg.create_oval(880, 510, 945, 575, fill="#FF9FC0", outline="")
        self.canvas_bg.lower("all")

        self.is_locked    = False
        self.button_map   = {}
        self.game_active  = True
        self.session_ended = False

        # Level & usia dari data anak
        age   = int(self.user["umur"])         if self.user and "umur"          in self.user else 7
        level = self.user["current_level"]     if self.user and "current_level" in self.user else "mudah"

        self.game     = GameManager(self.items, age=age, level=level, max_time=20*60)
        self.question = self.game.start_game()

        # ── Header ──────────────────────────────────────────────
        self.frame_header = tk.Frame(self.root, bg=HEADER_BG)
        self.frame_header.pack(fill="x")

        # Kiri: tombol berhenti
        frame_left = tk.Frame(self.frame_header, bg=HEADER_BG)
        frame_left.pack(side="left", padx=12, pady=8)

        self.stop_button = RoundedButton(
            frame_left,
            text="Berhenti",
            command=self.stop_game,
            width=120, height=36,
            bg_color="#D94040",
            hover_color="#B03030",
            font_spec=("Helvetica", 11, "bold")
        )
        self.stop_button.pack(side="left")

        # Kanan: timer + soal ke-N + progress
        frame_right = tk.Frame(self.frame_header, bg=HEADER_BG)
        frame_right.pack(side="right", padx=16, pady=6)

        # Pill timer
        self.timer_canvas = tk.Canvas(frame_right, width=150, height=34,
                                      bg=HEADER_BG, highlightthickness=0)
        self.timer_canvas.pack(side="top", anchor="e")
        self._timer_rect = make_rounded_rect(self.timer_canvas, 0, 0, 148, 32,
                                             r=16, fill=TIMER_OK, outline="")
        self._timer_text_id = self.timer_canvas.create_text(
            74, 16, text="20:00", fill="#ffffff",
            font=("Helvetica", 12, "bold")
        )

        # Progress "X/Y item dipilih"
        self.progress_label = tk.Label(
            frame_right,
            text="",
            font=("Helvetica", 10, "bold"),
            fg="#ffffff",
            bg=HEADER_BG
        )
        self.progress_label.pack(side="top", anchor="e", pady=(2, 0))

        # ── Baris soal ke-N (di bawah header, di atas kartu) ────
        self.frame_soal_info = tk.Frame(self.root, bg=BG)
        self.frame_soal_info.pack(fill="x", padx=20, pady=(6, 0))

        # Soal ke-N (kiri)
        self.soal_canvas = tk.Canvas(
            self.frame_soal_info,
            width=220, height=36,
            bg=BG, highlightthickness=0
        )
        self.soal_canvas.pack(side="left")
        self._soal_rect = make_rounded_rect(
            self.soal_canvas, 0, 0, 218, 34, r=17,
            fill=HEADER_BG, outline=""
        )
        self._soal_text = self.soal_canvas.create_text(
            109, 17, text="Soal  1 / 10",
            fill="#ffffff", font=("Helvetica", 12, "bold")
        )

        # Judul tengah: "Pilih satu gambar"
        title_text = "Pilih satu gambar" if self.mode == "picture" else "Pilih satu warna"
        tk.Label(
            self.frame_soal_info,
            text=title_text,
            font=("Helvetica", 20, "bold"),
            fg=HEADER_BG,
            bg=BG
        ).pack(side="left", expand=True)

        # Progress bar (kanan)
        self.progress_bar_frame = tk.Frame(self.frame_soal_info, bg=BG)
        self.progress_bar_frame.pack(side="right", padx=(0, 4))

        self.progress_bar_label = tk.Label(
            self.progress_bar_frame,
            text="",
            font=("Helvetica", 10),
            fg="#888888",
            bg=BG
        )
        self.progress_bar_label.pack(side="top", anchor="e")

        # Canvas untuk progress bar
        self.bar_canvas = tk.Canvas(
            self.progress_bar_frame,
            width=200, height=10,
            bg=BG, highlightthickness=0
        )
        self.bar_canvas.pack(side="top")
        # Track bar (abu)
        self.bar_canvas.create_rectangle(0, 0, 200, 10, fill="#E0E0E0", outline="", tags="track")
        # Fill bar (hijau) — update tiap soal
        self._bar_fill = self.bar_canvas.create_rectangle(0, 0, 0, 10,
                                                           fill=PROGRESS_OK, outline="",
                                                           tags="fill")

        # ── Area kartu gambar ────────────────────────────────────
        self.frame_game = tk.Frame(self.root, bg=BG)
        self.frame_game.pack(expand=True, pady=2)

        # ── Load gambar ──────────────────────────────────────────
        self.image_objects = {}
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        for name in self.items:
            try:
                path  = os.path.join(BASE_DIR, "assets", "images", f"{name}.png")
                image = Image.open(path).convert("RGBA").resize((112, 112))
                self.image_objects[name] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Gagal load gambar: {name} -> {e}")

        self.buttons = []
        self.render_question()
        self.update_timer()
        self.check_rfid()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ── Hardware ─────────────────────────────────────────────────
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
                if item in self.question:
                    self.handle_click(item)
                else:
                    print("Item tidak ada di soal sekarang")
            else:
                print("Kartu tidak terdaftar!")
        self.root.after(300, self.check_rfid)

    # ── Timer ─────────────────────────────────────────────────────
    def update_timer(self):
        if not self.game_active:
            return

        remaining = self.game.get_remaining_time()
        minutes   = remaining // 60
        seconds   = remaining % 60

        if remaining > 60:
            color = TIMER_OK
        elif remaining > 30:
            color = TIMER_WARN
        else:
            color = TIMER_CRIT

        self.timer_canvas.itemconfig(self._timer_rect, fill=color)
        self.timer_canvas.itemconfig(
            self._timer_text_id,
            text=f"{minutes:02}:{seconds:02}"
        )

        if remaining > 0:
            self.root.after(1000, self.update_timer)
        else:
            self.show_result(self.game.scoring.get_score())

    # ── Render soal ───────────────────────────────────────────────
    def render_question(self):
        for btn in self.buttons:
            btn.destroy()
        self.buttons.clear()
        self.button_map.clear()

        total_q    = self.game.episode_question_limit          # misal 10
        current_q  = self.game.completed_questions + 1         # soal ke-N
        selected   = len(self.game.current_selected_items)
        total_item = len(self.game.base_images)

        # ── Update "Soal ke-N / Total" ───────────────────────────
        self.soal_canvas.itemconfig(
            self._soal_text,
            text=f"Soal  {current_q} / {total_q}"
        )

        # ── Update progress bar episode ──────────────────────────
        pct = (self.game.completed_questions / total_q) if total_q > 0 else 0
        fill_w = int(200 * pct)
        self.bar_canvas.coords(self._bar_fill, 0, 0, fill_w, 10)
        self.progress_bar_label.config(
            text=f"{self.game.completed_questions}/{total_q} selesai"
        )

        # ── Update progress item soal aktif ──────────────────────
        self.progress_label.config(
            text=f"Dipilih: {selected} / {total_item}"
        )

        # ── Grid kartu ───────────────────────────────────────────
        cols = 4

        for index, item in enumerate(self.question):
            row = index // cols
            col = index % cols
            img = self.image_objects.get(item)

            card = tk.Canvas(
                self.frame_game,
                width=140, height=140,
                bg=BG, highlightthickness=0
            )
            # Shadow
            make_rounded_rect(card, 4, 4, 139, 139, r=16, fill=SHADOW, outline="")
            # Badan kartu
            rect_id = make_rounded_rect(card, 0, 0, 135, 135, r=16,
                                        fill=BTN_NORMAL, outline=BTN_BORDER, width=2)
            img_id = card.create_image(67, 67, image=img)
            card.image    = img
            card._rect_id = rect_id

            # Bind klik seluruh area kartu
            for tag in (rect_id, img_id):
                card.tag_bind(tag, "<Enter>",
                              lambda e, c=card: self._card_hover(c, True))
                card.tag_bind(tag, "<Leave>",
                              lambda e, c=card: self._card_hover(c, False))
                card.tag_bind(tag, "<Button-1>",
                              lambda e, i=item: self.handle_click(i))

            card.bind("<Enter>",    lambda e, c=card: self._card_hover(c, True))
            card.bind("<Leave>",    lambda e, c=card: self._card_hover(c, False))
            card.bind("<Button-1>", lambda e, i=item: self.handle_click(i))

            card.grid(row=row, column=col, padx=12, pady=10)
            self.buttons.append(card)
            self.button_map[item] = card

    def _card_hover(self, card, entering):
        if self.is_locked:
            return
        card.itemconfig(card._rect_id, fill="#F0F8FF" if entering else BTN_NORMAL)
        card.configure(cursor="hand2" if entering else "")

    # ── Klik / jawab ─────────────────────────────────────────────
    def handle_click(self, item):
        if self.is_locked:
            return

        result = self.game.select_item(item)
        if self.logger:
            self.logger.log(
                event="Pilih Kartu",
                round_no=self.game.current_round,
                level=self.game.level,
                score=self.game.scoring.get_score(),
                attempt=self.game.total_attempts,
                correct=result
            )
        print("RESULT:", result)

        if result:
            print("LED HIJAU NYALA")
            self.led.green_on()
        else:
            print("LED MERAH NYALA")
            self.led.red_on()

        card = self.button_map.get(item)
        if card:
            card.itemconfig(card._rect_id, fill=CORRECT if result else WRONG)

        if self.game.is_episode_finished():
            print("Episode selesai -> AI jalan")
            self.process_ai_episode()

        if self.game.is_game_over():
            self.show_result(self.game.scoring.get_score())
            return

        self.is_locked = True
        self.root.after(500, self.next_question)

    def next_question(self):
        if not self.game_active:
            return
        self.is_locked = False
        self.question  = self.game.current_question
        self.render_question()

    # ── Layar hasil ──────────────────────────────────────────────
    def show_result(self, score):
        if self.session_id and not self.session_ended:
            end_session(self.session_id, score, self.game.level)
            if self.user:
                print("Update level ke database:", self.game.level)
            self.session_ended = True
            print("Session ended with score:", score)
        
        if self.logger:
            self.logger.log(
                event="Game Selesai",
                round_no=self.game.current_round,
                level=self.game.level,
                score=self.game.scoring.get_score(),
                attempt=self.game.total_attempts,
                correct=""
            )
            self.logger.save() 

        self.game_active = False
        self.frame_header.destroy()
        self.frame_soal_info.destroy()
        self.frame_game.destroy()

        frame = tk.Frame(self.root, bg=BG)
        frame.place(relwidth=1, relheight=1)

        # Dekorasi gelembung hasil
        c_bg = tk.Canvas(frame, bg=BG, highlightthickness=0)
        c_bg.place(relwidth=1, relheight=1)
        c_bg.create_oval(-80, 350, 220, 650, fill=BUBBLE1, outline="")
        c_bg.create_oval(800, -80, 1100, 220, fill=BUBBLE2, outline="")
        c_bg.lower("all")

        # Kartu skor
        card_canvas = tk.Canvas(frame, width=420, height=320,
                                bg=BG, highlightthickness=0)
        card_canvas.place(relx=0.5, rely=0.47, anchor="center")

        make_rounded_rect(card_canvas, 5, 5, 419, 319, r=28, fill=SHADOW, outline="")
        make_rounded_rect(card_canvas, 0, 0, 414, 314, r=28,
                          fill="#ffffff", outline=HEADER_BG, width=2)

        # Banner atas kartu
        make_rounded_rect(card_canvas, 0, 0, 414, 70, r=28,
                          fill=HEADER_BG, outline="")
        card_canvas.create_rectangle(0, 40, 414, 70, fill=HEADER_BG, outline="")

        card_canvas.create_text(207, 35, text="Permainan Selesai!",
                                font=("Helvetica", 16, "bold"),
                                fill="#ffffff")

        card_canvas.create_text(207, 110, text="Skor kamu",
                                font=("Helvetica", 12),
                                fill="#888888")

        card_canvas.create_text(207, 185, text=str(score),
                                font=("Helvetica", 68, "bold"),
                                fill=SCORE_FG)

        # Bintang berdasarkan skor
        if score >= 80:
            stars = "* * *"
            star_color = "#F5A623"
        elif score >= 50:
            stars = "* *"
            star_color = "#F5A623"
        else:
            stars = "*"
            star_color = "#CCCCCC"

        card_canvas.create_text(207, 260, text=stars,
                                font=("Helvetica", 28, "bold"),
                                fill=star_color)

        # Tombol kembali ke menu
        btn = RoundedButton(
            frame,
            text="Kembali ke Menu",
            command=self.back_to_menu,
            width=220, height=48,
            bg_color=HEADER_BG,
            hover_color="#4070CC",
            font_spec=("Helvetica", 13, "bold")
        )
        btn.place(relx=0.5, rely=0.88, anchor="center")

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
        persentase = self.game.get_episode_performance()
        level      = self.game.level
        print("Performa:", persentase, "Level:", level)
        state      = get_state(level, persentase)
        action     = self.agent.choose_action(state)
        reward     = get_reward(persentase, level, action)
        new_level  = apply_action(level, action)
        print(f"[LEVEL UPDATE] {level} -> {new_level}")
        next_state = get_state(new_level, persentase)
        self.agent.learn(state, action, reward, next_state)
        if self.logger:
            self.logger.log(
                event="AI Update",
                round_no=self.game.current_round,
                level=new_level,
                score=self.game.scoring.get_score(),
                attempt=self.game.total_attempts,
                correct="",
                state=state,
                action=action,
                reward=reward,
                next_state=next_state
            )
        print(f"[AI] State: {state} -> Action: {action} -> Level baru: {new_level}")
        self.game.reset_episode(new_level)
