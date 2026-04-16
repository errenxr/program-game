import tkinter as tk
from ui.screens.menu_screen import MenuScreen
from ui.screens.game_screen import GameScreen

def start_game(mode):
    # 🔥 Hapus semua tampilan lama (menu)
    for widget in root.winfo_children():
        widget.destroy()

    # 🔥 Masuk ke game
    GameScreen(root, mode)

# root utama
root = tk.Tk()
root.title("Game Anak")
root.geometry("800x600")  # opsional biar konsisten

# tampilkan menu pertama kali
MenuScreen(root, start_game)

# jalankan aplikasi
root.mainloop()