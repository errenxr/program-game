import json
import os
import random
from datetime import datetime

from ai.config import LEARNING_RATE, DISCOUNT_FACTOR, EPSILON, ACTIONS
from ai.qlearning import update_q_value

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QTABLE_DIR = os.path.join(BASE_DIR, "user_qtables")
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "qtable_template.json")
LOG_DIR = os.path.join(BASE_DIR, "logs")


class Agent:
    def __init__(self, anak_id):
        self.anak_id = anak_id
        self.q_table = self.load_qtable()

    def load_qtable(self):
        path = os.path.join(QTABLE_DIR, f"anak_{self.anak_id}.json")

        if not os.path.exists(path):
            print("Q-table belum ada, pakai template")
            with open(TEMPLATE_PATH, "r") as f:
                q_table = json.load(f)
            self.save_qtable(q_table)
        else:
            with open(path, "r") as f:
                q_table = json.load(f)

        return q_table

    def save_qtable(self, q_table=None):
        if q_table is None:
            q_table = self.q_table

        path = os.path.join(QTABLE_DIR, f"anak_{self.anak_id}.json")
        with open(path, "w") as f:
            json.dump(q_table, f, indent=4)

    def choose_action(self, state):
        if random.uniform(0, 1) < EPSILON:
            action = random.choice(ACTIONS)  # eksplorasi
        else:
            # eksploitasi (ambil Q terbesar)
            state_actions = self.q_table[state]
            action = max(state_actions, key=state_actions.get)

        return action

    def learn(self, state, action, reward, next_state):
        new_q, old_q, max_future_q = update_q_value(
            self.q_table,
            state,
            action,
            reward,
            next_state,
            LEARNING_RATE,
            DISCOUNT_FACTOR,
            ACTIONS
        )

        self.save_qtable()

        self.log_learning(state, action, reward, old_q, new_q, max_future_q)


    def log_learning(self, state, action, reward, old_q, new_q, max_future_q):
        path = os.path.join(LOG_DIR, f"log_anak_{self.anak_id}.csv")

        file_exists = os.path.exists(path)

        with open(path, "a") as f:
            if not file_exists:
                f.write("timestamp,state,action,reward,old_q,new_q,max_future_q\n")

            f.write(f"{datetime.now()},{state},{action},{reward},{old_q},{new_q},{max_future_q}\n")