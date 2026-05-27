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
