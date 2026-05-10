import tkinter as tk
from ui.screens.menu_screen import MenuScreen
from ui.screens.game_screen import GameScreen
import time
import requests

def wait_server():
    while True:
        try:
            requests.get(
                "http://10.193.182.65:5000/api/get_current_user",
                timeout=3
            )
            print("Server connected")
            break

        except:
            print("Waiting Flask server...")
            time.sleep(5)

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