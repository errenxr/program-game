import time
from game.question import generate_base_images, shuffle_question
from game.validator import is_valid_choice
from game.scoring import Scoring


class GameManager:
    def __init__(self, images, age, level, max_time=15 * 60):
        self.images = images
        self.age = age
        self.level = level
        self.max_time = max_time  # dalam detik

        # waktu
        self.start_time = None

        # global game state
        self.current_round = 0
        self.scoring = Scoring()

        # soal aktif
        self.base_images = []
        self.current_question = []
        self.current_selected_items = []

        # statistik (opsional tapi bagus untuk TA)
        self.completed_questions = 0

    def start_game(self):
        self.start_time = time.time()
        self.current_round = 1
        self.scoring = Scoring()
        self.completed_questions = 0

        self.generate_new_question()
        return self.current_question

    def generate_new_question(self):
        self.base_images = generate_base_images(
            self.images, self.age, self.level
        )
        self.current_selected_items = []
        self.current_question = shuffle_question(self.base_images)

    def select_item(self, item):
        if self.is_game_over():
            return None

        # validasi (tidak boleh pilih yang sama dalam 1 soal)
        is_valid = is_valid_choice(item, self.current_selected_items)

        if is_valid:
            self.current_selected_items.append(item)

        # update skor
        self.scoring.update(is_valid)

        # cek apakah soal selesai
        if len(self.current_selected_items) == len(self.base_images):
            self.completed_questions += 1
            self.generate_new_question()
        else:
            # masih soal yang sama → hanya shuffle
            self.current_question = shuffle_question(self.base_images)

        self.current_round += 1

        return is_valid

    def is_game_over(self):
        if self.start_time is None:
            return False

        elapsed_time = time.time() - self.start_time
        return elapsed_time >= self.max_time

    def get_remaining_time(self):
        if self.start_time is None:
            return self.max_time

        elapsed = time.time() - self.start_time
        remaining = self.max_time - elapsed
        return max(0, int(remaining))

    # -----------------------------
    # STATE (UNTUK AI)
    # -----------------------------
    def get_state(self):
        return {
            "round": self.current_round,
            "score": self.scoring.get_score(),
            "selected_in_current": len(self.current_selected_items),
            "total_in_question": len(self.base_images),
            "completed_questions": self.completed_questions,
            "remaining_time": self.get_remaining_time(),
        }
    
    def get_result(self):
        return {
            "score": self.scoring.get_score(),
            "completed_questions": self.completed_questions,
            "time_spent": int(time.time() - self.start_time),
        }