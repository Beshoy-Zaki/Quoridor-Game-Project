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
        cfg = settings.get(difficulty, settings["medium"])

        # Record the current state in history before deciding
        ai_pos  = game.p1_pos if self.ai_id == 1 else game.p2_pos
        opp_pos = game.p2_pos if self.ai_id == 1 else game.p1_pos
        self._position_history.append((ai_pos, opp_pos))
        if len(self._position_history) > self._HISTORY_LEN:
            self._position_history.pop(0)

        if cfg["greedy"]:
            return self._greedy_move(game)

        if cfg.get("tt"):
            self._tt.clear()
            self._deadline = (
                time.perf_counter() + cfg["time_ms"] / 1000.0
                if cfg.get("time_ms") else None
            )
        else:
            self._deadline = None

        moves = self._generate_moves(game, use_walls=cfg["use_walls"])
        if not moves:
            return None

        moves = self._order_moves(game, moves, self.ai_id)

        best_score = -math.inf
        best_move  = None
        alpha, beta = -math.inf, math.inf

        if cfg.get("tt"):
            completed_best_move = None
            for depth in range(1, cfg["depth"] + 1):
                depth_best_score = -math.inf
                depth_best_move  = None
                local_alpha      = -math.inf

                for move in moves:
                    if self._deadline and time.perf_counter() >= self._deadline:
                        return completed_best_move if completed_best_move else best_move

                    cloned = copy.deepcopy(game)
                    self._apply_move(cloned, move)
                    score = self._minimax(
                        cloned,
                        depth=depth - 1,
                        alpha=local_alpha,
                        beta=beta,
                        maximizing_player=False,
                        ai_id=self.ai_id,
                        difficulty=difficulty,
                    )
                    if score > depth_best_score:
                        depth_best_score = score
                        depth_best_move  = move
                    local_alpha = max(local_alpha, depth_best_score)
                    if beta <= local_alpha:
                        break
                completed_best_move = depth_best_move
                best_score = depth_best_score
                best_move  = depth_best_move

            return best_move

        else:
            for move in moves:
                cloned = copy.deepcopy(game)
                self._apply_move(cloned, move)
                score = self._minimax(
                    cloned,
                    depth=cfg["depth"] - 1,
                    alpha=alpha,
                    beta=beta,
                    maximizing_player=False,
                    ai_id=self.ai_id,
                    difficulty=difficulty,
                )
                if score > best_score:
                    best_score = score
                    best_move  = move
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break

        return best_move

    def _greedy_move(self, game):
        moves = [("pawn", move) for move in game.get_legal_pawn_moves(self.ai_id)]
        if not moves:
            return None

        best_score = -math.inf
        best_move  = None
        for move in moves:
            cloned = copy.deepcopy(game)
            self._apply_move(cloned, move)
            score = self._evaluate_state(cloned, self.ai_id)
            if score > best_score:
                best_score = score
                best_move  = move
        return best_move

    def _minimax(self, game, depth, alpha, beta, maximizing_player, ai_id, difficulty):
        if self._deadline and time.perf_counter() >= self._deadline:
            return self._evaluate_state(game, ai_id, difficulty)
        if game.game_over or depth == 0:
            return self._evaluate_state(game, ai_id, difficulty)

        if difficulty == "extreme":
            key = self._state_key(game, maximizing_player)
            cached = self._tt.get(key)
            if cached is not None:
                cached_val, cached_flag, cached_depth = cached
                if cached_depth >= depth:
                    if cached_flag == "EXACT":
                        return cached_val
                    elif cached_flag == "LOWER":
                        alpha = max(alpha, cached_val)
                    elif cached_flag == "UPPER":
                        beta = min(beta, cached_val)
                    if alpha >= beta:
                        return cached_val

        moves = self._generate_moves(game, use_walls=True)
        moves = self._order_moves(game, moves, ai_id)
        if not moves:
            return self._evaluate_state(game, ai_id, difficulty)

        orig_alpha = alpha

        if maximizing_player:
            value = -math.inf
            for move in moves:
                cloned = copy.deepcopy(game)
                self._apply_move(cloned, move)
                value = max(
                    value,
                    self._minimax(cloned, depth - 1, alpha, beta, False, ai_id, difficulty),
                )
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
        else:
            value = math.inf
            for move in moves:
                cloned = copy.deepcopy(game)
                self._apply_move(cloned, move)
                value = min(
                    value,
                    self._minimax(cloned, depth - 1, alpha, beta, True, ai_id, difficulty),
                )
                beta = min(beta, value)
                if beta <= alpha:
                    break

        if difficulty == "extreme":
            if value <= orig_alpha:
                flag = "UPPER"
            elif value >= beta:
                flag = "LOWER"
            else:
                flag = "EXACT"
            self._tt[key] = (value, flag, depth)

        return value

    def _state_key(self, game, maximizing_player):
        # FIX 4 continued: depth removed from key
        board_key = tuple(tuple(row) for row in game.board)
        return (
            board_key,
            game.p1_pos,
            game.p2_pos,
            game.p1_walls,
            game.p2_walls,
            game.current_turn,
            maximizing_player,
        )

    def _generate_moves(self, game, use_walls=True):
        moves = [("pawn", move) for move in game.get_legal_pawn_moves(game.current_turn)]
        if not use_walls:
            return moves

        if (game.current_turn == 1 and game.p1_walls <= 0) or (
            game.current_turn == 2 and game.p2_walls <= 0
        ):
            return moves

        candidates = self._candidate_walls(game)
        for r, c in candidates:
            for orient in ("H", "V"):
                if self._is_valid_wall(game, r, c, orient):
                    moves.append(("wall", (r, c, orient)))
        return moves

    def _candidate_walls(self, game, limit=12):
        opp_pos    = game.p1_pos if game.current_turn == 2 else game.p2_pos
        candidates = set()
        for dr in range(-4, 5):
            for dc in range(-4, 5):
                r = opp_pos[0] + dr
                c = opp_pos[1] + dc
                if 0 <= r < 17 and 0 <= c < 17 and r % 2 == 1 and c % 2 == 1:
                    candidates.add((r, c))

        if len(candidates) < limit:
            for r in range(1, 16, 2):
                for c in range(1, 16, 2):
                    candidates.add((r, c))

        candidates = list(candidates)
        random.shuffle(candidates)
        return candidates[:limit]

    def _is_valid_wall(self, game, r, c, orient):
        if r % 2 == 0 or c % 2 == 0:
            return False
        cells = (
            [(r, c - 1), (r, c), (r, c + 1)]
            if orient == "H"
            else [(r - 1, c), (r, c), (r + 1, c)]
        )
        for rr, cc in cells:
            if not (0 <= rr < 17 and 0 <= cc < 17) or game.board[rr][cc] == 1:
                return False

        for rr, cc in cells:
            game.board[rr][cc] = 1

        has_path = game._has_path(game.p1_pos, game.p1_goal_row) and game._has_path(
            game.p2_pos, game.p2_goal_row
        )

        for rr, cc in cells:
            game.board[rr][cc] = 0

        return has_path
