# Quoridor Game
A fully featured implementation of the abstract strategy board game **Quoridor**, built with Python and Pygame. Includes a polished graphical interface, Human vs Human and Human vs AI game modes, multiple AI difficulty levels, and undo/redo functionality.

---

## Team Members

| Name | ID |
|---|---|
| Verina Hany Abdelmalek Mekhail | 2300394 |
| Beshoy Zaki Farouk Ayad | 2300069 |
| Mathew Mina Youssef Aziz | 2300910 |
| Kirollos Elkess Antonious Louiz Hanna | 2300411 |
| Mena Moheb Abdelshaheed | 2300700 |
| Abdalla Ragaee Ahmed Rateb | 2301025 |

---

## Game Description

Quoridor is a two-player abstract strategy game invented by Mirko Marchesi (1997) and winner of the Mensa Mind Game award. Each player controls a pawn that starts at the center of their baseline. The goal is to be the first to reach the opposite side of the board. On each turn a player may either move their pawn one square orthogonally, or place one wall (2 squares long) on the board to slow their opponent — but walls can never completely block a player's only path to the goal.

## Features

- **Human vs Human** — two players on the same machine
- **Human vs AI** — four difficulty levels (Easy / Medium / Hard / Extreme)
- **Graphical UI** — built with Pygame; board, pawns, walls, legal-move highlights, ghost-wall preview
- **Sidebar** — live wall counts, player positions, turn indicator, controls reference
- **Undo / Redo** — full move history with Ctrl+Z / Ctrl+Y (also accessible via sidebar buttons)
- **Path validation** — BFS ensures no wall placement can fully block a player's route
- **Restart & Menu navigation** — R key or sidebar button restarts; ESC returns to menu

---

## Installation

### Requirements

- Python 3.8 or higher
- Pygame

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/quoridor-cse472s.git
cd quoridor-cse472s

# 2. Install dependencies
pip install pygame

# 3. Run the game
python gui.py
```

---

## Project Structure

```
quoridor-cse472s/
├── gui.py          # Pygame graphical interface & main entry point
├── gameLogic.py    # Core game engine (board, rules, BFS path validation)
├── ailogic.py      # AI opponent (Minimax + Alpha-Beta pruning)
├── README.md
└── screenshots/    # Game screenshots (add yours here)
```

---

## Controls

| Input | Action |
|---|---|
| **Click a highlighted cell** | Move your pawn |
| **W** | Toggle wall placement mode |
| **H** | Set wall orientation to Horizontal |
| **V** | Set wall orientation to Vertical |
| **Space** | Toggle wall orientation (H ↔ V) |
| **Click on board** (wall mode) | Place wall at hovered position |
| **Ctrl + Z** | Undo last move |
| **Ctrl + Y** | Redo last undone move |
| **R** | Restart current game |
| **ESC** | Return to main menu |

---

## AI Implementation

The AI is implemented in `ailogic.py` using the **Minimax algorithm with Alpha-Beta pruning**.

### Difficulty Levels

| Level | Search Depth | Walls Used | Algorithm |
|---|---|---|---|
| Easy | 1 | No | Greedy (best immediate move) |
| Medium | 2 | Yes | Minimax + Alpha-Beta |
| Hard | 3 | Yes | Minimax + Alpha-Beta |
| Extreme | 4 | Yes | Iterative Deepening + Alpha-Beta + Transposition Table |

### Evaluation Function

Each board state is scored using:

```
score = (opponent_path_length − ai_path_length) × 10
      + (ai_walls_remaining − opponent_walls_remaining) × 2
      + center_column_bonus
      − repetition_penalty
```

- **Path length** is computed via BFS on the 17×17 internal board representation.
- **Repetition penalty** discourages the AI from revisiting recently occupied positions, preventing the oscillation (back-and-forth) behavior that can occur in endgame wall-less positions.
- **Extreme mode** uses a flag-based transposition table (EXACT / LOWER / UPPER bounds) and iterative deepening that only promotes a depth's result once that depth is fully searched, ensuring a timeout never returns a weaker move than Hard would.

### Board Representation

The board is modeled as a **17×17 grid** where:
- Even-indexed rows and columns represent playable cells.
- Odd-indexed rows and columns represent the gaps between cells where walls are placed.
- A value of `1` in a gap cell indicates a wall segment.

---

## Bonus Features Implemented

- ✅ **Undo / Redo** — full game history stack with redo support
- ✅ **Multiple AI difficulty levels** — Easy, Medium, Hard, Extreme

---

## References

- [Official Quoridor Rules](https://en.gigamic.com/files/media/fiche_pedagogique/educative-sheet_quoridor_en.pdf)
- [Quoridor on BoardGameGeek](https://boardgamegeek.com/boardgame/624/quoridor)
- [Minimax with Alpha-Beta Pruning — Wikipedia](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning)
- [Pygame Documentation](https://www.pygame.org/docs/)
- [BFS Pathfinding](https://en.wikipedia.org/wiki/Breadth-first_search)

---
