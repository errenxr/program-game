import tkinter as tk
from ui.screens.menu_screen import MenuScreen
from ui.screens.game_screen import GameScreen

def start_game(mode):
    for widget in root.winfo_children():
        widget.destroy()

    # masuk ke permainan
    GameScreen(root, mode)

# root utama
root = tk.Tk()
root.title("Game Anak")
root.geometry("800x600")  

MenuScreen(root, start_game)


root.mainloop()