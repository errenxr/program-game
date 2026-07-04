import csv
import os
from datetime import datetime


class ActivityLogger:

    def __init__(self, session_id, anak_id):

        self.session_id = session_id

        self.anak_id = anak_id

        self.logs = []

        self.session_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    def log(self,
            event,
            round_no,
            level,
            score,
            attempt,
            correct,
            state="",
            action="",
            reward="",
            next_state=""):

        self.logs.append({

            "timestamp": datetime.now().strftime("%H:%M:%S"),

            "event": event,

            "round": round_no,

            "level": level,

            "score": score,

            "attempt": attempt,

            "correct": correct,

            "state": state,

            "action": action,

            "reward": reward,

            "next_state": next_state

        })

    def save(self):

        os.makedirs("logs", exist_ok=True)

        filename = f"logs/anak_{self.anak_id}_session_{self.session_id}.csv"

        with open(filename,
                  "w",
                  newline="",
                  encoding="utf-8") as file:

            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "timestamp",
                    "event",
                    "round",
                    "level",
                    "score",
                    "attempt",
                    "correct",
                    "state",
                    "action",
                    "reward",
                    "next_state"
                ]
            )

            writer.writeheader()

            writer.writerows(self.logs)

        print("LOG disimpan:", filename)
