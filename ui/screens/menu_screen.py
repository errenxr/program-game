import tkinter as tk

# Palette
BG           = "#FFF8F0"
HEADER_BG    = "#FF9DC6"
ACCENT1      = "#FF6B9D"
ACCENT2      = "#FFD166"
TITLE_FG     = "#4A2060"
BUBBLE1      = "#FFD6E8"
BUBBLE2      = "#D6EEFF"
BUBBLE3      = "#D6FFE4"
CARD1_BG     = "#E8F4FF"
CARD1_BORDER = "#74B9FF"
CARD1_BTN    = "#4DABF7"
CARD1_HOVER  = "#339AF0"
CARD2_BG     = "#F3EEFF"
CARD2_BORDER = "#B197FC"
CARD2_BTN    = "#845EF7"
CARD2_HOVER  = "#7048E8"

# FIX: shadow tanpa transparansi
SHADOW       = "#D3D3D3"


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


class GameCard(tk.Canvas):
    def __init__(self, parent, icon, title, subtitle,
                 card_bg, border_color, btn_color, btn_hover,
                 command=None, **kwargs):
        super().__init__(parent, width=300, height=320,
                         bg=BG, highlightthickness=0, **kwargs)

        self.command = command
        self.btn_color = btn_color
        self.btn_hover = btn_hover

        # Shadow (FIX)
        make_rounded_rect(self, 6, 6, 299, 319, r=28,
                          fill=SHADOW, outline="")

        self._card_rect = make_rounded_rect(self, 0, 0, 293, 313, r=28,
                                            fill=card_bg,
                                            outline=border_color, width=2)

        self.create_text(147, 85, text=icon,
                         font=("Segoe UI Emoji", 52), anchor="center")

        self.create_text(147, 162, text=title,
                         font=("Nunito", 16, "bold"),
                         fill=TITLE_FG, anchor="center")

        self.create_text(147, 192, text=subtitle,
                         font=("Nunito", 11),
                         fill="#888888", anchor="center")

        self._btn_rect = make_rounded_rect(self, 50, 232, 244, 284, r=26,
                                           fill=btn_color, outline="")
        self._btn_text = self.create_text(147, 258,
                                          text="Main Sekarang! 🚀",
                                          font=("Nunito", 12, "bold"),
                                          fill="#ffffff", anchor="center")

        for tag in (self._card_rect, self._btn_rect, self._btn_text):
            self.tag_bind(tag, "<Enter>", self._on_enter)
            self.tag_bind(tag, "<Leave>", self._on_leave)
            self.tag_bind(tag, "<Button-1>", self._on_click)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _on_enter(self, _):
        self.itemconfig(self._btn_rect, fill=self.btn_hover)
        self.configure(cursor="hand2")

    def _on_leave(self, _):
        self.itemconfig(self._btn_rect, fill=self.btn_color)
        self.configure(cursor="")

    def _on_click(self, _):
        if self.command:
            self.command()


class MenuScreen:
    def __init__(self, root, start_game_callback=None):
        self.root = root
        self.start_game_callback = start_game_callback

        self.root.geometry("1024x600")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        # Background
        self.canvas_bg = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.canvas_bg.place(relwidth=1, relheight=1)

        self.canvas_bg.create_oval(-120, 360, 260, 740, fill=BUBBLE1, outline="")
        self.canvas_bg.create_oval(790, -130, 1160, 240, fill=BUBBLE2, outline="")
        self.canvas_bg.create_oval(400, 480, 600, 680, fill=BUBBLE3, outline="")

        # FIX: semua transparansi dihapus
        self.canvas_bg.create_oval(70, 80, 110, 120, fill="#FFE7A0", outline="")
        self.canvas_bg.create_oval(900, 500, 950, 550, fill="#FF9FC0", outline="")
        self.canvas_bg.create_oval(500, 50, 540, 90, fill="#A5D8FF", outline="")
        self.canvas_bg.create_oval(150, 480, 180, 510, fill="#D0BFFF", outline="")
        self.canvas_bg.create_oval(850, 200, 895, 245, fill=BUBBLE1, outline="")

        self.canvas_bg.lower("all")

        # Header
        header = tk.Frame(self.root, bg=HEADER_BG, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🧠  Focura  🧠",
            font=("Nunito", 18, "bold"),  # sedikit diperkecil
            fg="#ffffff",
            bg=HEADER_BG
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Main frame
        self.frame = tk.Frame(self.root, bg=BG)
        self.frame.pack(expand=True)

        tk.Label(
            self.frame,
            text="Pilih Permainan",
            font=("Nunito", 16, "bold"),
            bg=BG,
            fg=TITLE_FG
        ).pack(pady=(20, 6))

        tk.Label(
            self.frame,
            text="Latih ingatanmu dengan cara yang menyenangkan! 🌟",
            font=("Nunito", 12),
            bg=BG,
            fg="#999999"
        ).pack(pady=(0, 24))

        card_row = tk.Frame(self.frame, bg=BG)
        card_row.pack()

        GameCard(
            card_row,
            icon="🖼️",
            title="Pick The Picture",
            subtitle="Pilih gambar yang tepat!",
            card_bg=CARD1_BG,
            border_color=CARD1_BORDER,
            btn_color=CARD1_BTN,
            btn_hover=CARD1_HOVER,
            command=lambda: self.start_game("picture")
        ).grid(row=0, column=0, padx=36, pady=10)

        GameCard(
            card_row,
            icon="🎨",
            title="Pick The Color",
            subtitle="Pilih warna yang tepat!",
            card_bg=CARD2_BG,
            border_color=CARD2_BORDER,
            btn_color=CARD2_BTN,
            btn_hover=CARD2_HOVER,
            command=lambda: self.start_game("color")
        ).grid(row=0, column=1, padx=36, pady=10)

    def start_game(self, mode):
        self.frame.destroy()

        if self.start_game_callback:
            self.start_game_callback(mode)
        else:
            from ui.screens.game_screen import GameScreen
            GameScreen(self.root, mode)