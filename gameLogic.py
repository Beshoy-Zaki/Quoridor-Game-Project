import collections

class QuoridorEngine:
    def __init__(self, mode='multiplayer'):
        # 17x17 board: 0 = empty, 1 = wall
        self.board = [[0 for _ in range(17)] for _ in range(17)]
        # Player 1 (Bottom) starts at (16, 8), target is row 0
        self.p1_pos = (16, 8)
        self.p1_goal_row = 0
        self.p1_walls = 10
        # Player 2 (Top) starts at (0, 8), target is row 16
        self.p2_pos = (0, 8)
        self.p2_goal_row = 16
        self.p2_walls = 10
        self.current_turn = 1
        self.game_over = False
        self.winner = None
        self.mode = mode # 'single' or 'multiplayer'
        self._history = []
        self._redo_stack = []
        self._push_history()

    def _snapshot(self):
        return {
            "board": [row[:] for row in self.board],
            "p1_pos": self.p1_pos,
            "p2_pos": self.p2_pos,
            "p1_walls": self.p1_walls,
            "p2_walls": self.p2_walls,
            "current_turn": self.current_turn,
            "game_over": self.game_over,
            "winner": self.winner,
        }

    def _restore(self, snap):
        self.board = [row[:] for row in snap["board"]]
        self.p1_pos = snap["p1_pos"]
        self.p2_pos = snap["p2_pos"]
        self.p1_walls = snap["p1_walls"]
        self.p2_walls = snap["p2_walls"]
        self.current_turn = snap["current_turn"]
        self.game_over = snap["game_over"]
        self.winner = snap["winner"]

    def _push_history(self):
        self._history.append(self._snapshot())

    def undo(self):
        if len(self._history) <= 1:
            return False
        current = self._history.pop()
        self._redo_stack.append(current)
        self._restore(self._history[-1])
        return True

    def redo(self):
        if not self._redo_stack:
            return False
        snap = self._redo_stack.pop()
        self._history.append(snap)
        self._restore(snap)
        return True

    def get_legal_pawn_moves(self, player_id):
        r, c = self.p1_pos if player_id == 1 else self.p2_pos
        opp_r, opp_c = self.p2_pos if player_id == 1 else self.p1_pos
        moves = []

        # Directions: Up, Down, Left, Right
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        wall_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        perpendiculars = {
            (-2, 0): [(0, -2), (0, 2)], (2, 0): [(0, -2), (0, 2)],
            (0, -2): [(-2, 0), (2, 0)], (0, 2): [(-2, 0), (2, 0)]
        }

        for i in range(4):
            dr, dc = directions[i]
            wr, wc = wall_offsets[i]
            tr, tc = r + dr, c + dc
            wall_r, wall_c = r + wr, c + wc

            if not (0 <= tr < 17 and 0 <= tc < 17): continue
            if self.board[wall_r][wall_c] == 1: continue

            if (tr, tc) == (opp_r, opp_c):
                sr, sc = tr + dr, tc + dc
                swr, swc = tr + wr, tc + wc
                if 0 <= sr < 17 and 0 <= sc < 17 and self.board[swr][swc] == 0:
                    moves.append((sr, sc))
                else:
                    for p_dr, p_dc in perpendiculars[(dr, dc)]:
                        diag_r, diag_c = tr + p_dr, tc + p_dc
                        diag_wall_r, diag_wall_c = tr + (p_dr // 2), tc + (p_dc // 2)
                        if 0 <= diag_r < 17 and 0 <= diag_c < 17:
                            if self.board[diag_wall_r][diag_wall_c] == 0:
                                moves.append((diag_r, diag_c))
            else:
                moves.append((tr, tc))
        return moves

    def move_pawn(self, row, col):
        legal_moves = self.get_legal_pawn_moves(self.current_turn)
        if (row, col) not in legal_moves: return False
        self._redo_stack.clear()
        if self.current_turn == 1:
            self.p1_pos = (row, col)
            if row == self.p1_goal_row: self.winner = 1
        else:
            self.p2_pos = (row, col)
            if row == self.p2_goal_row: self.winner = 2
        if self.winner is not None: self.game_over = True
        self._switch_turn()
        self._push_history()
        return True

    def place_wall(self, r, c, orient):
        if (self.current_turn == 1 and self.p1_walls <= 0) or \
           (self.current_turn == 2 and self.p2_walls <= 0): return False

        if r % 2 == 0 or c % 2 == 0: return False
        cells = [(r, c-1), (r, c), (r, c+1)] if orient == 'H' else [(r-1, c), (r, c), (r+1, c)]
        for rr, cc in cells:
            if not (0 <= rr < 17 and 0 <= cc < 17) or self.board[rr][cc] == 1: return False

        for rr, cc in cells: self.board[rr][cc] = 1
        if self._has_path(self.p1_pos, self.p1_goal_row) and self._has_path(self.p2_pos, self.p2_goal_row):
            self._redo_stack.clear()
            if self.current_turn == 1: self.p1_walls -= 1
            else: self.p2_walls -= 1
            self._switch_turn()
            self._push_history()
            return True
        for rr, cc in cells: self.board[rr][cc] = 0
        return False

    def _switch_turn(self):
        if not self.game_over: self.current_turn = 2 if self.current_turn == 1 else 1

    def _has_path(self, start, goal_row):
        queue = collections.deque([start])
        visited = {start}
        while queue:
            r, c = queue.popleft()
            if r == goal_row: return True
            for dr, dc, wr, wc in [(-2,0,-1,0), (2,0,1,0), (0,-2,0,-1), (0,2,0,1)]:
                tr, tc, w_r, w_c = r+dr, c+dc, r+wr, c+wc
                if 0 <= tr < 17 and 0 <= tc < 17 and self.board[w_r][w_c] == 0 and (tr, tc) not in visited:
                    visited.add((tr, tc))
                    queue.append((tr, tc))
        return False
