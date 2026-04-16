import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from game.game_manager import GameManager

# Dummy data (sementara, nanti dari database)
IMAGES = ["kucing", "mobil", "apel", "bola", "ikan", "ayam", "jeruk"]


def main():
    print("=== SIMULASI GAME PICK THE PICTURE ===")

    # input user
    age = int(input("Masukkan umur (5/6/7): "))
    level = input("Pilih level (mudah/sedang/susah): ").lower()

    # gunakan waktu pendek dulu untuk testing
    game = GameManager(IMAGES, age=age, level=level, max_time=60)

    # mulai game
    question = game.start_game()

    # loop sampai waktu habis
    while not game.is_game_over():

        print("\n==============================")
        print(f"Ronde ke-{game.current_round}")
        print(f"Sisa waktu: {game.get_remaining_time()} detik")
        print(f"Skor: {game.scoring.get_score()}")
        print(f"Soal ke-{game.completed_questions + 1}")

        # tampilkan progress dalam 1 soal
        print(
            f"Progress soal: {len(game.current_selected_items)}/"
            f"{len(game.base_images)}"
        )

        print("Pilihan gambar:", question)

        # input (simulasi RFID)
        choice = input("Pilih gambar: ").strip().lower()

        # validasi input
        if choice not in question:
            print("⚠️ Pilihan tidak valid, pilih dari daftar!")
            continue

        # proses pilihan
        result = game.select_item(choice)

        if result is True:
            print("✅ Benar")
        elif result is False:
            print("❌ Salah (sudah dipilih dalam soal ini)")
        else:
            print("⏰ Waktu habis!")
            break

        # ambil soal terbaru (bisa sama / baru)
        question = game.current_question

    # =============================
    # HASIL AKHIR
    # =============================
    print("\n==============================")
    print("⏰ WAKTU HABIS!")
    print("HASIL AKHIR:")

    result = game.get_result()

    print(f"Skor akhir: {result['score']}")
    print(f"Jumlah soal selesai: {result['completed_questions']}")
    print(f"Durasi bermain: {result['time_spent']} detik")

    print("==============================")


if __name__ == "__main__":
    main()