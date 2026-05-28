import sys
import pygame

from gameLogic import QuoridorEngine
from ailogic import QuoridorAI

CELL_SIZE = 58
GAP_SIZE = 12
MARGIN = 30
SIDEBAR_W = 220
def _build_offsets():
    offsets = [0] * 17
    for i in range(1, 17):
        prev_size = CELL_SIZE if (i - 1) % 2 == 0 else GAP_SIZE
        offsets[i] = offsets[i - 1] + prev_size
    return offsets


OFFSETS = _build_offsets()
BOARD_PX = OFFSETS[16] + CELL_SIZE
WIN_W = MARGIN * 2 + BOARD_PX + SIDEBAR_W
WIN_H = MARGIN * 2 + BOARD_PX

C_BG = (30, 30, 35)
C_BOARD_BG = (45, 38, 30)
C_CELL = (62, 50, 38)
C_CELL_BORDER = (80, 65, 50)
C_HIGHLIGHT = (120, 210, 80)
C_HIGHLIGHT_A = (80, 160, 50, 140)
C_P1 = (220, 80, 60)
C_P2 = (60, 140, 220)
C_WALL_PLACED = (210, 175, 80)
C_WALL_GHOST = (210, 175, 80, 100)
C_WALL_BAD = (210, 60, 60, 120)
C_SIDEBAR_BG = (22, 22, 28)
C_TEXT_MAIN = (230, 225, 215)
C_TEXT_DIM = (130, 120, 110)
C_P1_TEXT = (240, 110, 90)
C_P2_TEXT = (90, 170, 240)
C_BTN_BG = (55, 55, 65)
C_BTN_HOVER = (75, 75, 90)
C_BTN_TEXT = (210, 210, 220)
C_WIN_BG = (25, 50, 30)
C_WIN_TEXT = (160, 240, 130)
C_ERROR_TEXT = (230, 80, 80)
C_TURN_BAR_P1 = (80, 30, 25)
C_TURN_BAR_P2 = (20, 45, 80)
C_WALL_MODE = (200, 160, 50)

FONT_BIG = 26
FONT_MED = 19
FONT_SMALL = 15
FPS = 60

def logical_to_screen(row, col):
    sx = MARGIN + OFFSETS[col]
    sy = MARGIN + OFFSETS[row]
    return sx, sy


def logical_size(row_or_col):
    return CELL_SIZE if row_or_col % 2 == 0 else GAP_SIZE


def cell_center(row, col):
    sx, sy = logical_to_screen(row, col)
    cx = sx + CELL_SIZE // 2
    cy = sy + CELL_SIZE // 2
    return cx, cy


def screen_to_logical(px, py):
    bx = px - MARGIN
    by = py - MARGIN

    if bx < 0 or by < 0 or bx >= BOARD_PX or by >= BOARD_PX:
        return None

    col = _find_logical_index(bx)
    row = _find_logical_index(by)

    if col is None or row is None:
        return None

    return row, col


def _find_logical_index(pixel_offset):
    for i in range(17):
        size = CELL_SIZE if i % 2 == 0 else GAP_SIZE
        if OFFSETS[i] <= pixel_offset < OFFSETS[i] + size:
            return i
    return None


def snap_wall_center(row, col):
    wr = row if row % 2 == 1 else row - 1
    wc = col if col % 2 == 1 else col - 1

    if not (1 <= wr <= 15 and 1 <= wc <= 15):
        return None
    return wr, wc


def draw_board_background(surface):
    board_rect = pygame.Rect(
        MARGIN - 6, MARGIN - 6, BOARD_PX + 12, BOARD_PX + 12
    )
    pygame.draw.rect(surface, C_BOARD_BG, board_rect, border_radius=6)


def draw_cells(surface):
    for row in range(0, 17, 2):
        for col in range(0, 17, 2):
            sx, sy = logical_to_screen(row, col)
            cell_rect = pygame.Rect(sx, sy, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, C_CELL, cell_rect, border_radius=3)
            pygame.draw.rect(surface, C_CELL_BORDER, cell_rect, width=1, border_radius=3)


def draw_row_col_labels(surface, font_small):
    cell_num = 0
    for col in range(0, 17, 2):
        sx, _ = logical_to_screen(0, col)
        label = font_small.render(str(cell_num), True, C_TEXT_DIM)
        surface.blit(label, (sx + CELL_SIZE // 2 - label.get_width() // 2, MARGIN - 20))
        cell_num += 1

    cell_num = 0
    for row in range(0, 17, 2):
        _, sy = logical_to_screen(row, 0)
        label = font_small.render(str(cell_num), True, C_TEXT_DIM)
        surface.blit(label, (MARGIN - 22, sy + CELL_SIZE // 2 - label.get_height() // 2))
        cell_num += 1


def draw_placed_walls(surface, board):
    for row in range(17):
        for col in range(17):
            if board[row][col] == 1:
                sx, sy = logical_to_screen(row, col)
                w = logical_size(col)
                h = logical_size(row)
                wall_rect = pygame.Rect(sx, sy, w, h)
                pygame.draw.rect(surface, C_WALL_PLACED, wall_rect, border_radius=2)

def draw_highlights(surface, legal_moves):
    for (row, col) in legal_moves:
        cx, cy = cell_center(row, col)
        pygame.draw.circle(surface, C_HIGHLIGHT, (cx, cy), CELL_SIZE // 5)
        pygame.draw.circle(surface, C_BG, (cx, cy), CELL_SIZE // 5 - 4)
        pygame.draw.circle(surface, C_HIGHLIGHT, (cx, cy), CELL_SIZE // 5, width=3)


def draw_pawn(surface, row, col, colour, label):
    cx, cy = cell_center(row, col)
    radius = CELL_SIZE // 2 - 6

    shadow_offset = 3
    pygame.draw.circle(surface, (15, 15, 15), (cx + shadow_offset, cy + shadow_offset), radius)

    pygame.draw.circle(surface, colour, (cx, cy), radius)

    shine_x = cx - radius // 3
    shine_y = cy - radius // 3
    pygame.draw.circle(surface, _lighten(colour, 60), (shine_x, shine_y), radius // 4)

    font = pygame.font.SysFont("Arial", FONT_MED, bold=True)
    txt = font.render(label, True, (255, 255, 255))
    surface.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))


def draw_ghost_wall(surface, wall_row, wall_col, orientation, is_legal):
    if orientation == "H":
        cells = [(wall_row, wall_col - 1), (wall_row, wall_col), (wall_row, wall_col + 1)]
    else:
        cells = [(wall_row - 1, wall_col), (wall_row, wall_col), (wall_row + 1, wall_col)]

    colour = C_WALL_GHOST if is_legal else C_WALL_BAD

    ghost_surf = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)

    for (r, c) in cells:
        if not (0 <= r < 17 and 0 <= c < 17):
            continue
        sx, sy = logical_to_screen(r, c)
        w = logical_size(c)
        h = logical_size(r)
        pygame.draw.rect(ghost_surf, colour, pygame.Rect(sx, sy, w, h), border_radius=2)

    surface.blit(ghost_surf, (0, 0))
def draw_sidebar(surface, game, mode, difficulty, error_msg, wall_orient, fonts):
    font_big, font_med, font_small = fonts

    sidebar_rect = pygame.Rect(MARGIN * 2 + BOARD_PX, 0, SIDEBAR_W, WIN_H)
    pygame.draw.rect(surface, C_SIDEBAR_BG, sidebar_rect)

    x = MARGIN * 2 + BOARD_PX + 15
    y = 18

    title = font_big.render("QUORIDOR", True, C_TEXT_MAIN)
    surface.blit(title, (x, y))
    y += title.get_height() + 4

    mode_str = "Human vs AI" if mode == "single" else "Human vs Human"
    mode_label = font_small.render(mode_str, True, C_TEXT_DIM)
    surface.blit(mode_label, (x, y))
    y += mode_label.get_height() + 18

    pygame.draw.line(surface, C_TEXT_DIM, (x, y), (x + SIDEBAR_W - 30, y))
    y += 12

    if not game.game_over:
        bar_colour = C_TURN_BAR_P1 if game.current_turn == 1 else C_TURN_BAR_P2
        bar_rect = pygame.Rect(x - 15, y, SIDEBAR_W - 5, 36)
        pygame.draw.rect(surface, bar_colour, bar_rect, border_radius=4)

        turn_text = f"PLAYER {game.current_turn}'S TURN"
        turn_colour = C_P1_TEXT if game.current_turn == 1 else C_P2_TEXT
        turn_label = font_med.render(turn_text, True, turn_colour)
        surface.blit(turn_label, (x, y + 8))
        y += 46
    else:
        y += 10

    for pid, pawn_colour, text_colour in [(1, C_P1, C_P1_TEXT), (2, C_P2, C_P2_TEXT)]:
        walls_left = game.p1_walls if pid == 1 else game.p2_walls
        pos = game.p1_pos if pid == 1 else game.p2_pos

        pygame.draw.circle(surface, pawn_colour, (x + 8, y + 10), 8)

        player_label = font_med.render(f"     Player {pid}", True, text_colour)
        surface.blit(player_label, (x, y))
        y += player_label.get_height() + 2

        walls_label = font_small.render(f"    Walls: {walls_left}", True, C_TEXT_MAIN)
        surface.blit(walls_label, (x, y))
        y += walls_label.get_height() + 2

        pos_label = font_small.render(f"    Pos: ({pos[0]//2}, {pos[1]//2})", True, C_TEXT_DIM)
        surface.blit(pos_label, (x, y))
        y += pos_label.get_height() + 12

    pygame.draw.line(surface, C_TEXT_DIM, (x, y), (x + SIDEBAR_W - 30, y))
    y += 12

    mode_colour = C_WALL_MODE if wall_orient else C_TEXT_DIM
    wmode_label = font_small.render("WALL MODE: " + ("ON" if wall_orient else "OFF"), True, mode_colour)
    surface.blit(wmode_label, (x, y))
    y += wmode_label.get_height() + 4

    if wall_orient:
        orient_label = font_small.render(f"Orientation: {wall_orient}", True, C_WALL_MODE)
        surface.blit(orient_label, (x, y))
    y += font_small.get_height() + 12

    pygame.draw.line(surface, C_TEXT_DIM, (x, y), (x + SIDEBAR_W - 30, y))
    y += 10

    controls_title = font_small.render("CONTROLS", True, C_TEXT_DIM)
    surface.blit(controls_title, (x, y))
    y += controls_title.get_height() + 6

    controls = [
        "Click cell: move",
        "W key: walls",
        "H/V: orient",
        "Click: place",
        "Ctrl+Z: undo",
        "Ctrl+Y: redo",
        "R: restart",
        "ESC: menu",
    ]

    col_width = (SIDEBAR_W - 30) // 2
    line_h = font_small.get_height() + 4
    for idx, line in enumerate(controls):
        col = idx % 2
        row = idx // 2
        lbl = font_small.render(line, True, C_TEXT_DIM)
        surface.blit(lbl, (x + col * col_width, y + row * line_h))

    y += ((len(controls) + 1) // 2) * line_h + 8

    if mode == "single" and difficulty:
        pygame.draw.line(surface, C_TEXT_DIM, (x, y), (x + SIDEBAR_W - 30, y))
        y += 10
        diff_label = font_small.render(f"AI: {difficulty.upper()}", True, C_P2_TEXT)
        surface.blit(diff_label, (x, y))
        y += diff_label.get_height() + 8

    if error_msg:
        pygame.draw.line(surface, C_TEXT_DIM, (x, y), (x + SIDEBAR_W - 30, y))
        y += 8
        err_label = font_small.render("! " + error_msg, True, C_ERROR_TEXT)
        surface.blit(err_label, (x, y))
        y += err_label.get_height() + 6

    if game.game_over:
        button_top = WIN_H - 144
        win_y = min(y + 12, button_top - 70)
        pygame.draw.line(surface, C_TEXT_DIM, (x, win_y - 12), (x + SIDEBAR_W - 30, win_y - 12))
        win_bg = pygame.Rect(x - 15, win_y, SIDEBAR_W - 5, 50)
        pygame.draw.rect(surface, C_WIN_BG, win_bg, border_radius=6)
        win_txt = font_big.render(f"P{game.winner} WINS!", True, C_WIN_TEXT)
        surface.blit(win_txt, (x, win_y + 12))

    mouse_pos = pygame.mouse.get_pos()

    undo_rect = pygame.Rect(x - 5, WIN_H - 144, (SIDEBAR_W - 24) // 2, 32)
    redo_rect = pygame.Rect(undo_rect.right + 4, WIN_H - 144, (SIDEBAR_W - 24) // 2, 32)
    restart_rect = pygame.Rect(x - 5, WIN_H - 96, SIDEBAR_W - 20, 38)

    undo_colour = C_BTN_HOVER if undo_rect.collidepoint(mouse_pos) else C_BTN_BG
    redo_colour = C_BTN_HOVER if redo_rect.collidepoint(mouse_pos) else C_BTN_BG
    restart_colour = C_BTN_HOVER if restart_rect.collidepoint(mouse_pos) else C_BTN_BG

    pygame.draw.rect(surface, undo_colour, undo_rect, border_radius=6)
    pygame.draw.rect(surface, redo_colour, redo_rect, border_radius=6)
    pygame.draw.rect(surface, restart_colour, restart_rect, border_radius=6)

    undo_txt = font_small.render("UNDO", True, C_BTN_TEXT)
    redo_txt = font_small.render("REDO", True, C_BTN_TEXT)
    restart_txt = font_med.render("RESTART  [R]", True, C_BTN_TEXT)

    surface.blit(
        undo_txt,
        (
            undo_rect.x + (undo_rect.w - undo_txt.get_width()) // 2,
            undo_rect.y + (undo_rect.h - undo_txt.get_height()) // 2,
        ),
    )
    surface.blit(
        redo_txt,
        (
            redo_rect.x + (redo_rect.w - redo_txt.get_width()) // 2,
            redo_rect.y + (redo_rect.h - redo_txt.get_height()) // 2,
        ),
    )
    surface.blit(
        restart_txt,
        (
            restart_rect.x + (restart_rect.w - restart_txt.get_width()) // 2,
            restart_rect.y + (restart_rect.h - restart_txt.get_height()) // 2,
        ),
    )

    return {
        "undo": undo_rect,
        "redo": redo_rect,
        "restart": restart_rect,
    }


def draw_goal_lines(surface):
    sx0, sy0 = logical_to_screen(0, 0)
    sx1, _ = logical_to_screen(0, 16)
    goal_top_rect = pygame.Rect(sx0 - 3, sy0 - 3, sx1 - sx0 + CELL_SIZE + 6, 4)
    pygame.draw.rect(surface, C_P1, goal_top_rect, border_radius=2)

    sx0, sy0 = logical_to_screen(16, 0)
    sx1, _ = logical_to_screen(16, 16)
    goal_bot_rect = pygame.Rect(sx0 - 3, sy0 + CELL_SIZE - 1, sx1 - sx0 + CELL_SIZE + 6, 4)
    pygame.draw.rect(surface, C_P2, goal_bot_rect, border_radius=2)


def get_clicked_pawn_cell(mouse_pos):
    result = screen_to_logical(mouse_pos[0], mouse_pos[1])
    if result is None:
        return None
    row, col = result
    if row % 2 == 0 and col % 2 == 0:
        return row, col
    return None


def get_hovered_wall_center(mouse_pos, orientation):
    result = screen_to_logical(mouse_pos[0], mouse_pos[1])
    if result is None:
        return None

    row, col = result

    if row % 2 == 0:
        row = max(1, row - 1)
    if col % 2 == 0:
        col = max(1, col - 1)

    if not (1 <= row <= 15 and 1 <= col <= 15):
        return None

    return row, col


def is_wall_legal_preview(game, wall_row, wall_col, orientation):
    if orientation == "H":
        cells = [(wall_row, wall_col - 1), (wall_row, wall_col), (wall_row, wall_col + 1)]
    else:
        cells = [(wall_row - 1, wall_col), (wall_row, wall_col), (wall_row + 1, wall_col)]

    for (r, c) in cells:
        if not (0 <= r < 17 and 0 <= c < 17):
            return False
        if game.board[r][c] == 1:
            return False

    walls_left = game.p1_walls if game.current_turn == 1 else game.p2_walls
    return walls_left > 0

def _lighten(colour, amount):
    return tuple(min(255, c + amount) for c in colour)


def make_fonts():
    font_big = pygame.font.SysFont("Arial", FONT_BIG, bold=True)
    font_med = pygame.font.SysFont("Arial", FONT_MED, bold=False)
    font_small = pygame.font.SysFont("Arial", FONT_SMALL, bold=False)
    return font_big, font_med, font_small


def get_ai_move(game, difficulty, ai):
    move = ai.get_best_move(game, difficulty=difficulty)
    if move is None:
        return ("move", *game.get_legal_pawn_moves(2)[0])

    kind, payload = move
    if kind == "pawn":
        r, c = payload
        return ("move", r, c)

    r, c, orient = payload
    return ("wall", r, c, orient)

def run_menu(screen, fonts):
    font_big, font_med, font_small = fonts
    clock = pygame.time.Clock()

    btn_w, btn_h = 260, 48
    cx = WIN_W // 2

    def make_btn(label, y):
        rect = pygame.Rect(cx - btn_w // 2, y, btn_w, btn_h)
        return rect, label

    buttons = [
        make_btn("Human vs Human", 200),
        make_btn("vs AI  -  Easy", 268),
        make_btn("vs AI  -  Medium", 336),
        make_btn("vs AI  -  Hard", 404),
        make_btn("vs AI  -  Extreme", 472),
    ]

    while True:
        screen.fill(C_BG)
        mouse_pos = pygame.mouse.get_pos()

        title1 = font_big.render("QUORIDOR", True, C_TEXT_MAIN)
        title2 = font_small.render("CSE472s  Spring 2026  |  Team Project", True, C_TEXT_DIM)
        screen.blit(title1, (cx - title1.get_width() // 2, 120))
        screen.blit(title2, (cx - title2.get_width() // 2, 155))

        subtitle = font_med.render("Select Game Mode", True, C_TEXT_DIM)
        screen.blit(subtitle, (cx - subtitle.get_width() // 2, 175))

        for rect, label in buttons:
            colour = C_BTN_HOVER if rect.collidepoint(mouse_pos) else C_BTN_BG
            pygame.draw.rect(screen, colour, rect, border_radius=8)
            txt = font_med.render(label, True, C_BTN_TEXT)
            screen.blit(
                txt,
                (rect.x + (rect.w - txt.get_width()) // 2, rect.y + (rect.h - txt.get_height()) // 2),
            )

        footer = font_small.render("Click a button to start", True, C_TEXT_DIM)
        screen.blit(footer, (cx - footer.get_width() // 2, WIN_H - 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, (rect, _) in enumerate(buttons):
                    if rect.collidepoint(event.pos):
                        if i == 0:
                            return "multiplayer", None
                        if i == 1:
                            return "single", "easy"
                        if i == 2:
                            return "single", "medium"
                        if i == 3:
                            return "single", "hard"
                        return "single", "extreme"

        pygame.display.flip()
        clock.tick(FPS)


def run_game(screen, fonts, mode, difficulty):
    font_big, font_med, font_small = fonts
    clock = pygame.time.Clock()

    game = QuoridorEngine(mode=mode)
    ai = QuoridorAI(ai_id=2) if mode == "single" else None

    wall_mode = False
    wall_orient = None
    error_msg = ""
    error_timer = 0
    legal_moves = game.get_legal_pawn_moves(game.current_turn)

    while True:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        if mode == "single" and game.current_turn == 2 and not game.game_over:
            pygame.display.set_caption("Quoridor  |  AI is thinking…")
            _render_frame(
                screen,
                game,
                mode,
                difficulty,
                error_msg,
                wall_mode,
                wall_orient,
                None,
                legal_moves,
                fonts,
            )
            pygame.display.flip()

            action = get_ai_move(game, difficulty, ai)
            _apply_ai_action(game, action)
            legal_moves = game.get_legal_pawn_moves(game.current_turn)
            pygame.display.set_caption("Quoridor")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"

                if event.key == pygame.K_r:
                    return "restart"

                if event.key == pygame.K_z and (event.mod & pygame.KMOD_CTRL):
                    if game.undo():
                        if mode == "single" and game.current_turn == 2:
                            game.undo()
                        legal_moves = game.get_legal_pawn_moves(game.current_turn)
                        error_msg = ""

                if event.key == pygame.K_y and (event.mod & pygame.KMOD_CTRL):
                    if game.redo():
                        if mode == "single" and game.current_turn == 2:
                            game.redo()
                        legal_moves = game.get_legal_pawn_moves(game.current_turn)
                        error_msg = ""

                if event.key == pygame.K_w and not game.game_over:
                    wall_mode = not wall_mode
                    wall_orient = "H" if wall_mode else None
                    legal_moves = game.get_legal_pawn_moves(game.current_turn)

                if event.key == pygame.K_h and wall_mode:
                    wall_orient = "H"
                if event.key == pygame.K_v and wall_mode:
                    wall_orient = "V"

                if event.key == pygame.K_SPACE and wall_mode:
                    wall_orient = "V" if wall_orient == "H" else "H"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                btn_rects = _get_sidebar_btn_rects()
                if btn_rects["restart"].collidepoint(mouse_pos):
                    return "restart"
                if btn_rects["undo"].collidepoint(mouse_pos):
                    if game.undo():
                        if mode == "single" and game.current_turn == 2:
                            game.undo()
                        legal_moves = game.get_legal_pawn_moves(game.current_turn)
                        error_msg = ""
                    continue
                if btn_rects["redo"].collidepoint(mouse_pos):
                    if game.redo():
                        if mode == "single" and game.current_turn == 2:
                            game.redo()
                        legal_moves = game.get_legal_pawn_moves(game.current_turn)
                        error_msg = ""
                    continue

                if game.game_over:
                    continue

                if mode == "single" and game.current_turn == 2:
                    continue

                if wall_mode and wall_orient:
                    wc = get_hovered_wall_center(mouse_pos, wall_orient)
                    if wc is not None:
                        wr, wcol = wc
                        success = game.place_wall(wr, wcol, wall_orient)
                        if success:
                            error_msg = ""
                            legal_moves = game.get_legal_pawn_moves(game.current_turn)
                        else:
                            error_msg = "Invalid wall placement!"
                            error_timer = 180
                    else:
                        error_msg = "Click on the board to place wall"
                        error_timer = 120
                else:
                    clicked = get_clicked_pawn_cell(mouse_pos)
                    if clicked is not None:
                        row, col = clicked
                        success = game.move_pawn(row, col)
                        if success:
                            error_msg = ""
                            legal_moves = game.get_legal_pawn_moves(game.current_turn)
                        else:
                            error_msg = "Invalid move!"
                            error_timer = 120
                    else:
                        result = screen_to_logical(mouse_pos[0], mouse_pos[1])
                        if result is not None:
                            error_msg = "Press W to enter wall mode"
                            error_timer = 120

        if error_timer > 0:
            error_timer -= 1
        else:
            error_msg = ""

        ghost_wall = None
        if wall_mode and wall_orient and not game.game_over:
            wc = get_hovered_wall_center(mouse_pos, wall_orient)
            if wc is not None:
                ghost_wall = (wc[0], wc[1], wall_orient)

        _render_frame(
            screen,
            game,
            mode,
            difficulty,
            error_msg,
            wall_mode,
            wall_orient,
            ghost_wall,
            legal_moves,
            fonts,
        )
        pygame.display.flip()

    return "menu"


def _apply_ai_action(game, action):
    if action[0] == "move":
        _, r, c = action
        game.move_pawn(r, c)
    elif action[0] == "wall":
        _, r, c, orient = action
        success = game.place_wall(r, c, orient)
        if not success:
            moves = game.get_legal_pawn_moves(2)
            if moves:
                game.move_pawn(*moves[0])


def _get_sidebar_btn_rects():
    x = MARGIN * 2 + BOARD_PX + 15 - 5
    return {
        "undo": pygame.Rect(x, WIN_H - 144, (SIDEBAR_W - 24) // 2, 32),
        "redo": pygame.Rect(x + (SIDEBAR_W - 24) // 2 + 4, WIN_H - 144, (SIDEBAR_W - 24) // 2, 32),
        "restart": pygame.Rect(x, WIN_H - 96, SIDEBAR_W - 20, 38),
    }


def _render_frame(
    screen,
    game,
    mode,
    difficulty,
    error_msg,
    wall_mode,
    wall_orient,
    ghost_wall,
    legal_moves,
    fonts,
):
    screen.fill(C_BG)

    draw_board_background(screen)
    draw_cells(screen)
    draw_goal_lines(screen)
    draw_row_col_labels(screen, fonts[2])
    draw_placed_walls(screen, game.board)

    if not wall_mode and not game.game_over:
        draw_highlights(screen, legal_moves)

    if ghost_wall is not None:
        wr, wc, orient = ghost_wall
        legal_preview = is_wall_legal_preview(game, wr, wc, orient)
        draw_ghost_wall(screen, wr, wc, orient, legal_preview)

    draw_pawn(screen, game.p1_pos[0], game.p1_pos[1], C_P1, "1")
    draw_pawn(screen, game.p2_pos[0], game.p2_pos[1], C_P2, "2")

    draw_sidebar(
        screen,
        game,
        mode,
        difficulty,
        error_msg,
        wall_orient if wall_mode else None,
        fonts,
    )


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Quoridor  |  CSE472s")
    fonts = make_fonts()

    while True:
        mode, difficulty = run_menu(screen, fonts)

        if mode is None:
            break

        result = run_game(screen, fonts, mode, difficulty)

        if result == "restart":
            result = run_game(screen, fonts, mode, difficulty)
            while result == "restart":
                result = run_game(screen, fonts, mode, difficulty)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
