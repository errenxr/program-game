import time
from game.question import generate_base_images, shuffle_question
from game.validator import is_valid_choice
from game.scoring import Scoring


class GameManager:
    def __init__(self, images, age, level, max_time=20 * 60):
        self.images = images
        self.age = age
        self.level = level
        self.max_time = max_time  # detik

        # waktu
        self.start_time = None

        # global game state
        self.current_round = 0
        self.scoring = Scoring()

        # soal aktif
        self.base_images = []
        self.current_question = []
        self.current_selected_items = []

        # statistik
        self.completed_questions = 0

        # episode (untuk AI)
        self.episode_question_limit = 10
        self.correct_answers = 0
        self.total_attempts = 0
        self.episode_finished = False

    def start_game(self):
        self.start_time = time.time()
        self.current_round = 1
        self.scoring = Scoring()

        self.completed_questions = 0
        self.correct_answers = 0
        self.total_attempts = 0
        self.episode_finished = False

        self.generate_new_question()
        return self.current_question

    def generate_new_question(self):
        self.base_images = generate_base_images(
            self.images, self.age, self.level
        )
        self.current_selected_items = []
        self.current_question = shuffle_question(self.base_images)

    def select_item(self, item):
        if self.is_game_over() or self.episode_finished:
            return None

        self.total_attempts += 1

        # validasi pilihan
        is_valid = is_valid_choice(item, self.current_selected_items)

        if is_valid:
            self.current_selected_items.append(item)
            self.correct_answers += 1

        # update skor global
        self.scoring.update(is_valid)

        # cek apakah 1 soal selesai
        if len(self.current_selected_items) == len(self.base_images):
            self.completed_questions += 1

            # cek apakah episode selesai
            if self.completed_questions >= self.episode_question_limit:
                self.episode_finished = True
            else:
                self.generate_new_question()
        else:
            # masih soal yang sama → shuffle ulang
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

    def is_episode_finished(self):
        return self.episode_finished

    def get_episode_performance(self):
        """
        Menggunakan akurasi:
        benar / total attempt
        """
        if self.total_attempts == 0:
            return 0
        return (self.correct_answers / self.total_attempts) * 100

    def reset_episode(self, new_level):
        """
        Dipanggil setelah AI menentukan level baru
        """
        self.level = new_level

        self.completed_questions = 0
        self.correct_answers = 0
        self.total_attempts = 0
        self.episode_finished = False

        self.generate_new_question()

    def get_state(self):
        return {
            "round": self.current_round,
            "score": self.scoring.get_score(),
            "completed_questions": self.completed_questions,
            "correct_answers": self.correct_answers,
            "total_attempts": self.total_attempts,
            "accuracy": self.get_episode_performance(),
            "remaining_time": self.get_remaining_time(),
            "level": self.level
        }

    def get_result(self):
        return {
            "score": self.scoring.get_score(),
            "completed_questions": self.completed_questions,
            "accuracy": self.get_episode_performance(),
            "time_spent": int(time.time() - self.start_time),
            "level": self.level
        }