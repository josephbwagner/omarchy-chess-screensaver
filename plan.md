# Omarchy Chess Screensaver — Developer Spec

## Overview

A terminal chess screensaver for [Omarchy](https://omarchy.org/) that replaces the default ASCII art screensaver. It replays elite Grandmaster games from the Lichess Elite Database at 1 move per second, displaying an animated chess board with game metadata and a running move log.

Intended to be open-sourced and shared with the broader Omarchy community.

---

## Repository

**Path:** `~/repos/omarchy-chess-screensaver`  
**Git:** Yes, initialized as a git repo from the start  
**Visibility:** Public (designed for community sharing)

---

## Technology Stack

- **Language:** Python 3.14+ (system Python at `/usr/bin/python3`)
- **Dependency manager:** [`uv`](https://docs.astral.sh/uv/) — fast, self-contained, installs to `~/.local/bin/uv` with no system packages touched
- **Project format:** `pyproject.toml` — defines dependencies; `uv sync` creates a `.venv/` inside the repo
- **Key dependency:** [`python-chess`](https://python-chess.readthedocs.io/) — PGN parsing, board state, move application
- **Terminal rendering:** Python `curses` (standard library) — fullscreen layout, color, input
- **No system-level pip installs.** All Python dependencies are isolated in `.venv/` within the repo.

---

## Data

### Source
Lichess Elite Database (PGN format) — monthly PGN files containing games played by 2200+ rated players.

### Bundled Subset
Include a curated selection totaling **< 100 MB** stored in `data/pgn/`:
- All files from 2013, 2014, 2015 (~6 MB total)
- 2016 files January through May (~74 MB total)
- **Total: ~80 MB**

These represent the early era of Lichess elite games and contain thousands of high-quality games.

### Game Selection at Runtime
- Pick a **random PGN file** from `data/pgn/`
- Pick a **random game** from within that file (seek to a random offset, then find the next game header)
- No Elo filtering — any game in the database is eligible

### Error Handling
- Malformed or unreadable PGN files/games: **silently skip** and load a new random game
- No logging, no user-visible error messages

---

## Screen Layout

The screensaver runs fullscreen in the terminal. The entire screen is wrapped in a **decorative ASCII border** (using `─`, `│`, `┌`, `┐`, `└`, `┘` box-drawing characters).

```
┌──────────────────────────────────────────────────────────────┐
│                              │  MATCH INFO                   │
│       CHESS BOARD            │  ─────────────────────────    │
│       (left 2/3)             │  [player names, elo, etc.]    │
│                              │                               │
│                              │  MOVE LOG                     │
│                              │  ─────────────────────────    │
│                              │  1. e4  e5                    │
│                              │  2. Nf3 Nc6                   │
│                              │  3. Bb5 ...                   │
└──────────────────────────────────────────────────────────────┘
```

### Board Panel (Left ~2/3 of interior width)
- Centered vertically and horizontally in its column
- Board is 8×8 squares; each square is rendered as **3 characters wide × 1 character tall** (e.g., ` ♙ ` or ` · ` or ` ░ `)
- Rank labels (8–1) on the left side of the board
- File labels (a–h) along the bottom of the board
- A vertical divider (`│`) separates the board panel from the info panel

### Info Panel (Right ~1/3 of interior width)

**Top section — Match Info:**
```
  White: Magnus Carlsen (2882)
  Black: Hikaru Nakamura (2736)

  Opening: Sicilian Defense
  Time Control: 3+0 (Blitz)
  Date: 2016-03-14
  Result: 1-0
```

**Bottom section — Move Log:**
- Header: `MOVES` with a divider line
- Moves displayed as standard algebraic notation pairs:
  ```
  1.  e4    e5
  2.  Nf3   Nc6
  3.  Bb5   a6
  ...
  ```
- Fixed-width columns for move number, white move, black move
- Scrolls upward as moves are added — most recent move always visible at the bottom
- The active (just-played) move is highlighted

---

## Chess Board Rendering

### Orientation
Always from **White's perspective** (rank 1 at bottom, rank 8 at top).

### Square Colors
- **Light squares:** `·` (middle dot, U+00B7)
- **Dark squares:** `░` (light shade block, U+2591)
- When no piece occupies a square, the square character fills the 3-char cell: ` · ` or ` ░ `

### Piece Symbols (Unicode)
| Piece  | White | Black |
|--------|-------|-------|
| King   | ♔     | ♚     |
| Queen  | ♕     | ♛     |
| Rook   | ♖     | ♜     |
| Bishop | ♗     | ♝     |
| Knight | ♘     | ♞     |
| Pawn   | ♙     | ♟     |

Pieces are centered in their 3-char cell, e.g., ` ♙ ` on a light square or ` ♚ ` on a dark square.

### Move Highlighting
After each move, the **source square** and **destination square** are wrapped in brackets:
- Example: `[♙]` or `[·]` (piece or empty square)
- Both the from-square and to-square use bracket highlighting for the duration of that move's display

---

## Animation & Game Flow

### Move Pacing
- Default: **1 move per second** (1.0s between each half-move/ply)
- Configurable via `--speed FLOAT` flag (seconds per move, e.g., `--speed 0.5` for 2 moves/sec)

### Game Lifecycle
1. Load a random game from a random PGN file
2. Display initial board position (starting position) with match info
3. Play through moves one at a time at the configured speed
4. After each move: update board, update move log, update highlighted squares
5. **On game end:**
   - Display the final board position
   - "Fade" the board: progressively replace pieces with their square characters over ~1 second (pieces disappear, leaving just the empty board pattern)
   - Show the result prominently in the match info panel (e.g., `★ 1-0 White wins ★`)
   - Pause for ~3 seconds
   - Load next random game and repeat

---

## Colors & Theme

The screensaver uses **ANSI terminal color codes** (colors 0–15) only. The terminal is already configured with the active Omarchy theme's color palette, so colors automatically inherit the theme.

### Color Assignments (ANSI roles)
- **Foreground text:** default terminal foreground (color 7/15)
- **Board border & dividers:** bright black / dim (color 8)
- **Match info labels:** color 6 (cyan equivalent — mapped to theme's secondary)
- **Match info values:** color 7 (white/foreground)
- **Move log — played moves:** color 7
- **Move log — current/active move:** color 3 (yellow/accent — highlighted)
- **Board light squares:** default foreground
- **Board dark squares:** color 8 (bright black / dim)
- **White pieces:** color 15 (bright white)
- **Black pieces:** color 8 or color 0+bold (dim/dark)
- **Highlighted move squares (brackets):** color 3 (yellow/accent)
- **Game result display:** color 2 (green) for win, color 1 (red) for loss, color 3 (yellow) for draw
- **Background:** always terminal default black (color 0)

---

## Omarchy Integration

### How It Runs
The screensaver is launched by Omarchy's `omarchy-launch-screensaver` command, which opens a fullscreen terminal window with class `org.omarchy.screensaver` and runs `omarchy-cmd-screensaver`.

### Override Strategy
The install script adds `~/repos/omarchy-chess-screensaver/bin` to the front of `PATH` via a clearly-marked, sentinel-guarded block in `~/.bashrc` / `~/.zshrc`. The binary is named `omarchy-cmd-screensaver`, which shadows the stock Omarchy command.

**System impact is minimal and fully documented:**
| Change | Location | Reversible? |
|--------|----------|-------------|
| PATH entry (one block) | `~/.bashrc` and/or `~/.zshrc` | Yes — `uninstall.sh` removes it |
| Python virtualenv | `~/repos/omarchy-chess-screensaver/.venv/` | Yes — `uninstall.sh` offers to remove it |
| `uv` binary (if auto-installed) | `~/.local/bin/uv` | Yes — `rm ~/.local/bin/uv` |

No system packages modified. No Omarchy source files touched. No new services or daemons.

### Exit Behavior
- **Any key press** exits the screensaver immediately (matching stock Omarchy behavior)
- Implemented via `curses` non-blocking input check in the main loop

---

## Repository Structure

```
omarchy-chess-screensaver/
├── bin/
│   └── omarchy-cmd-screensaver      # Shell wrapper: exec uv run python -m chess_screensaver
├── src/
│   └── chess_screensaver/
│       ├── __init__.py
│       ├── __main__.py              # Entry point: arg parsing, curses init/cleanup
│       ├── renderer.py              # curses-based screen rendering
│       ├── board.py                 # Board ASCII/Unicode rendering logic
│       ├── game_loader.py           # PGN parsing and random game selection
│       ├── layout.py                # Terminal size calculations, panel geometry
│       └── animation.py            # Fade effect, timing, game lifecycle
├── data/
│   └── pgn/
│       ├── lichess_elite_2013-09.pgn
│       ├── ...                      # All 2013-2015 files + 2016 Jan-May
│       └── lichess_elite_2016-05.pgn
├── pyproject.toml                   # Project metadata and dependencies (python-chess)
├── install.sh                       # Installs uv if needed, uv sync, adds one PATH line
├── uninstall.sh                     # Removes the PATH line, optionally removes .venv
└── README.md
```

---

## `bin/omarchy-cmd-screensaver`

A **shell wrapper script** (not a Python file). Its only job is to locate the project root and invoke Python via `uv run`:

```bash
#!/bin/bash
# Resolve the project root (one level up from bin/)
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
exec uv run --project "$PROJECT_ROOT" python -m chess_screensaver "$@"
```

- `chmod +x`
- `uv run` handles virtualenv activation automatically
- Passes all CLI args (e.g., `--speed`) through to the Python module
- No hardcoded paths — works regardless of where the repo is cloned

---

## `pyproject.toml`

```toml
[project]
name = "chess-screensaver"
version = "0.1.0"
description = "A chess screensaver for Omarchy"
requires-python = ">=3.10"
dependencies = [
    "chess>=1.10",
]

[project.scripts]
omarchy-chess-screensaver = "chess_screensaver.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/chess_screensaver"]
```

---

## `install.sh`

**Principle: minimal, documented, reversible. Makes exactly two changes to the system.**

```bash
#!/usr/bin/env bash
set -e
```

Steps performed:

1. **Check for `uv`** — if not installed, install it via the official installer:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   This installs `uv` to `~/.local/bin/uv`. Nothing else is modified.

2. **Run `uv sync`** in the project root — creates `.venv/` inside the repo with `python-chess` installed. No system Python packages are touched.

3. **Add PATH entry** — append a clearly-marked block to `~/.bashrc` (and `~/.zshrc` if it exists):
   ```bash
   # >>> omarchy-chess-screensaver >>>
   export PATH="$HOME/repos/omarchy-chess-screensaver/bin:$PATH"
   # <<< omarchy-chess-screensaver <<<
   ```
   Script checks for the sentinel comment before adding (idempotent — safe to run twice).

4. **Print summary** of exactly what was changed, and instructions to reload shell.

**That's it. No other files are created or modified.**

---

## `uninstall.sh`

```bash
#!/usr/bin/env bash
set -e
```

Steps performed:

1. **Remove PATH block** from `~/.bashrc` and `~/.zshrc` using `sed` to delete lines between the sentinel comments (inclusive).

2. **Optionally remove `.venv/`** — prompt the user:
   ```
   Remove .venv/ (Python virtualenv inside repo)? [y/N]
   ```

3. Print confirmation of what was removed.

**Does not remove `uv` itself** (user may use it for other things). Documents in output that `uv` can be removed manually with `rm ~/.local/bin/uv` if desired.

---

## `README.md`

Should include:
- What it is (brief description + one-line elevator pitch)
- Screenshot or ASCII mockup of the layout
- **Prerequisites:** `uv` (auto-installed by `install.sh` if missing), Python 3.10+, Omarchy with hypridle configured
- **Install:**
  ```bash
  git clone https://github.com/<user>/omarchy-chess-screensaver ~/repos/omarchy-chess-screensaver
  cd ~/repos/omarchy-chess-screensaver
  ./install.sh
  # Then open a new terminal or: source ~/.bashrc
  ```
- **Verify:**
  ```bash
  which omarchy-cmd-screensaver   # should show .../omarchy-chess-screensaver/bin/...
  omarchy-cmd-screensaver --help
  ```
- **Uninstall:**
  ```bash
  cd ~/repos/omarchy-chess-screensaver
  ./uninstall.sh
  # Then open a new terminal or: source ~/.bashrc
  # Optionally: rm -rf ~/repos/omarchy-chess-screensaver
  ```
- **Configuration:** `--speed FLOAT` flag (default 1.0 seconds per move). Document how this is passed through from `omarchy-launch-screensaver` if users want to customize it (they'd need to create a wrapper or modify hypridle config — document this clearly).
- **What install.sh changes:** Be explicit. Exactly two changes: (1) `.venv/` created inside the repo, (2) one PATH block added to `~/.bashrc`/`~/.zshrc`.
- **Adding more games:** Drop additional `.pgn` files into `data/pgn/` — the screensaver picks from all files in that directory.
- **Credits:** Lichess Elite Database (Creative Commons CC0 public domain)
- **Troubleshooting:** What to do if screensaver doesn't activate, unicode doesn't render, etc.

---

## Implementation Notes for Developer

1. **PGN random seek:** The PGN files are large. Rather than loading all games into memory, seek to a random byte offset in the file, scan forward to the next `[Event` header, and parse from there. Use `python-chess`'s `chess.pgn.read_game()` for parsing.

2. **Terminal size handling:** Use `curses.LINES` and `curses.COLS` for dynamic layout. Recalculate panel widths on `KEY_RESIZE`. The board is always 8×8 squares at 3 chars wide × 1 char tall = 24 chars wide minimum for the board itself (plus rank labels = 26 chars). The board panel should be `max(26, floor(COLS * 2/3))` wide.

3. **Board render loop:** On each move, only redraw changed squares (from-square, to-square) plus the move log panel — avoid full-screen redraws for performance.

4. **Fade effect:** On game end, iterate through all board squares and replace pieces with empty square characters (`·` or `░`) with a short delay (~50ms per piece) in a random order.

5. **Input handling:** Use `stdscr.nodelay(True)` + `stdscr.getch()` in the main loop to check for keypresses without blocking. Return value `-1` means no key pressed.

6. **Signal handling:** Trap `SIGINT` and `SIGTERM` to ensure curses cleanup runs (cursor restore, terminal mode reset) before exit.

7. **python-chess board → display:** Use `board.piece_at(square)` to get pieces for rendering. Squares are numbered 0–63, a1=0, h8=63. For white's perspective: iterate ranks 7 down to 0, files 0 to 7.
