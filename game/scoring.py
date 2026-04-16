class Scoring:
    def __init__(self):
        self.score = 0

    def update(self, correct):
        if correct:
            self.score += 1
        else:
            self.score -= 1

    def get_score(self):
        return self.score