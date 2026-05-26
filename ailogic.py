import copy
import math
import random
import time


class QuoridorAI:
    def __init__(self, ai_id=2):
        self.ai_id = ai_id
        self._tt = {}
        self._deadline = None
        self._position_history = []
        self._HISTORY_LEN = 6

    def get_best_move(self, game, difficulty="medium"):
        difficulty = difficulty.lower()
        settings = {
            "easy":    {"depth": 1, "use_walls": False, "greedy": True},
            "medium":  {"depth": 2, "use_walls": True,  "greedy": False},
            "hard":    {"depth": 3, "use_walls": True,  "greedy": False},
            "extreme": {"depth": 4, "use_walls": True,  "greedy": False,
                        "tt": True, "time_ms": 800},
        }
