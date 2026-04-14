# Omarchy Chess Screensaver

A terminal chess screensaver for [Omarchy](https://omarchy.org/) that replays elite Grandmaster games from the Lichess Elite Database — one move per second, fullscreen, with live move log and match metadata.

```
┌──────────────────────────────────────────────────────────────────────┐
│                              │ MATCH INFO                            │
│  8  ♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜  │ ────────────────────────────           │
│  7  ♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟  │ White: Magnus Carlsen (2882)          │
│  6   ░  ·  ░  ·  ░  ·  ░  · │ Black: Hikaru Nakamura (2736)         │
│  5   ·  ░  ·  ░  ·  ░  ·  ░ │                                       │
│  4   ░  ·  ░  ·  ░  ·  ░  · │ Opening: Sicilian Defense             │
│  3   ·  ░  ·  ░  ·  ░  ·  ░ │ Time: 3+0 (Blitz)                    │
│  2  ♙ ♙ ♙ ♙ ♙ ♙ ♙ ♙  │ Date: 2016.03.14                      │
│  1  ♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖  │ Result: 1-0                           │
│      a  b  c  d  e  f  g  h  │                                       │
│                              │ MOVES                                 │
│                              │ ────────────────────────────          │
│                              │   1. e4      e5                       │
│                              │   2. Nf3     Nc6                      │
│                              │   3. Bb5     a6                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

- **Python 3.10+** — system Python at `/usr/bin/python3`
- **[uv](https://docs.astral.sh/uv/)** — auto-installed by `install.sh` if missing
- **Omarchy** with `hypridle` configured to invoke `omarchy-cmd-screensaver`
- A terminal that supports Unicode and 256 colors (any modern terminal does)

---

## Install

```bash
git clone https://github.com/<user>/omarchy-chess-screensaver ~/repos/omarchy-chess-screensaver
cd ~/repos/omarchy-chess-screensaver
./install.sh
# Then reload your shell:
source ~/.bashrc
```

### What `install.sh` changes

Exactly **two** changes are made to your system:

| Change | Location | Reversible? |
|--------|----------|-------------|
| Python virtualenv (`.venv/`) | Inside the repo | Yes — `uninstall.sh` offers to remove it |
| One `PATH` block | `~/.bashrc` (and `~/.zshrc` if present) | Yes — `uninstall.sh` removes it |

No system packages are installed. No Omarchy source files are touched. No daemons or services are created.

---

## Verify

```bash
which omarchy-cmd-screensaver   # should show .../omarchy-chess-screensaver/bin/...
omarchy-cmd-screensaver --help
```

---

## Uninstall

```bash
cd ~/repos/omarchy-chess-screensaver
./uninstall.sh
source ~/.bashrc
# Optionally remove the repo entirely:
# rm -rf ~/repos/omarchy-chess-screensaver
```

`uninstall.sh` does **not** remove `uv` (you may use it for other projects). To remove it manually:
```bash
rm ~/.local/bin/uv
```

---

## Configuration

### Speed

Default playback is **1 move per second**. Pass `--speed SECONDS` to change it:

```bash
omarchy-cmd-screensaver --speed 0.5   # 2 moves per second
omarchy-cmd-screensaver --speed 2.0   # 1 move every 2 seconds
```

### Customizing for Omarchy / hypridle

`omarchy-launch-screensaver` runs `omarchy-cmd-screensaver` from `PATH`. To pass a custom speed, create a thin wrapper in `~/repos/omarchy-chess-screensaver/bin/`:

```bash
# bin/omarchy-cmd-screensaver (override with custom speed)
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
exec uv run --project "$PROJECT_ROOT" python -m chess_screensaver --speed 0.5 "$@"
```

Or edit your `hypridle` configuration to invoke the command with a flag directly.

---

## Adding more games

Drop any additional Lichess PGN files into `data/pgn/`. The screensaver picks randomly from every `.pgn` file it finds in that directory.

Lichess Elite Database files are available at:
https://database.nikonoel.fr/ (mirror) or via Lichess database exports.

---

## Bundled data

The repository includes a curated subset of the [Lichess Elite Database](https://database.nikonoel.fr/):
- All games from 2013, 2014, and 2015
- January–May 2016

These are games played by 2200+ rated players, published under the **Creative Commons CC0 (public domain)** license.

---

## Troubleshooting

**Screensaver doesn't activate**
- Verify `which omarchy-cmd-screensaver` points to this repo's `bin/`.
- Make sure you reloaded your shell (`source ~/.bashrc`) after installing.
- Check that `hypridle` is configured and running.

**Unicode chess pieces don't render**
- Ensure your terminal uses a font with Unicode support (e.g., JetBrains Mono Nerd Font, Fira Code).
- Check `LANG` / `LC_ALL` are set to a UTF-8 locale (`echo $LANG` should show something like `en_US.UTF-8`).

**Colors look wrong**
- Omarchy's terminal color theme is applied automatically. If the terminal emulator is not using an Omarchy theme, colors may differ from intended.
- The screensaver uses only ANSI colors 0–15, so it respects whatever theme is active.

**"Terminal too small" message**
- Resize the terminal to at least 50 columns × 13 lines.
- Under Omarchy, the screensaver window is typically fullscreen.

---

## Credits

- **Lichess Elite Database** — [database.nikonoel.fr](https://database.nikonoel.fr/) — CC0 Public Domain
- **python-chess** — [python-chess.readthedocs.io](https://python-chess.readthedocs.io/)
- **uv** — [docs.astral.sh/uv](https://docs.astral.sh/uv/)
