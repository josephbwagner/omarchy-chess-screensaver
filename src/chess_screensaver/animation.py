import curses
import random
import time
from pathlib import Path

import chess

from .game_loader import load_random_game
from .layout import calculate_layout
from .renderer import Renderer

# Path to the bundled PGN data directory (two levels up from this package)
_DATA_DIR = str(Path(__file__).parent.parent.parent / 'data')


def run_screensaver(stdscr, speed):
    """Main screensaver loop — called inside curses.wrapper()."""
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.clear()

    renderer = Renderer(stdscr)

    while True:
        if _check_quit(stdscr):
            return

        game = _load_next_game(stdscr, renderer)
        if game is None:
            continue

        result = _play_game(stdscr, renderer, game, speed)
        if result == 'quit':
            return

        # Brief pause after game ends before loading the next
        if _timed_wait(stdscr, 3.0):
            return


# ---------------------------------------------------------------------------
# Game loading
# ---------------------------------------------------------------------------

def _load_next_game(stdscr, renderer):
    """Attempt to load a random game, retrying silently until one is found."""
    for _ in range(20):
        if _check_quit(stdscr):
            return None
        game = load_random_game(_DATA_DIR)
        if game is not None:
            return game
        time.sleep(0.05)
    return None


# ---------------------------------------------------------------------------
# Game playback
# ---------------------------------------------------------------------------

def _play_game(stdscr, renderer, game, speed):
    """
    Play through all moves of a game, updating the display at each ply.
    Returns 'quit' if the user pressed a key, 'next' otherwise.
    """
    board    = chess.Board()
    metadata = _extract_metadata(game)

    # Collect moves up front so we can iterate without mutating the game tree
    moves = []
    node  = game
    while node.variations:
        node = node.variations[0]
        moves.append(node.move)

    if not moves:
        return 'next'

    move_log  = []  # list of (num, white_san, black_san)
    highlight = None

    layout = calculate_layout(curses.LINES, curses.COLS)

    if _wipe_board(stdscr, renderer, board, metadata, layout):
        return 'quit'

    if _timed_wait(stdscr, speed):
        return 'quit'

    for ply, move in enumerate(moves):
        if _check_quit(stdscr):
            return 'quit'

        # Handle terminal resize
        if curses.LINES != layout['lines'] or curses.COLS != layout['cols']:
            layout = calculate_layout(curses.LINES, curses.COLS)

        from_sq = move.from_square
        to_sq   = move.to_square
        san     = board.san(move)

        # Phase 1 — "lift": show piece at source with destination marked
        # Duration is 25% of the move speed (e.g. 0.5s at a 2s pace)
        renderer.draw_full(board, metadata, move_log, (from_sq, to_sq), layout)
        if _timed_wait(stdscr, speed * 0.25):
            return 'quit'

        board.push(move)

        move_num = ply // 2 + 1
        if ply % 2 == 0:
            # White's move — start a new pair
            move_log.append((move_num, san, ''))
        else:
            # Black's move — fill in the second half of the current pair
            prev = move_log[-1]
            move_log[-1] = (prev[0], prev[1], san)

        # Phase 2 — "land": show piece at destination
        highlight = (from_sq, to_sq)
        renderer.draw_full(board, metadata, move_log, highlight, layout)

        if _timed_wait(stdscr, speed):
            return 'quit'

    # ── Game over ──────────────────────────────────────────────────────
    result_display = _format_result(metadata.get('result', '*'))
    layout = calculate_layout(curses.LINES, curses.COLS)
    renderer.draw_full(board, metadata, move_log, None, layout,
                       result_display=result_display)

    if _fade_board(stdscr, renderer, board, metadata, move_log, layout, result_display):
        return 'quit'

    return 'next'


# ---------------------------------------------------------------------------
# Wipe-in effect
# ---------------------------------------------------------------------------

def _wipe_board(stdscr, renderer, board, metadata, layout):
    """
    Reveal the starting position with a left-to-right column wipe (file a → h).
    Returns True if the user pressed a key.
    """
    occupied = [sq for sq in chess.SQUARES if board.piece_at(sq) is not None]
    if not occupied:
        return False

    # Group squares by file (0 = a … 7 = h)
    by_file: list[list[int]] = [[] for _ in range(8)]
    for sq in occupied:
        by_file[chess.square_file(sq)].append(sq)

    faded: set[int] = set(occupied)  # start fully hidden

    delay = 0.08  # seconds between each column reveal

    for file_idx in range(8):
        if _check_quit(stdscr):
            return True
        faded -= set(by_file[file_idx])
        renderer.draw_full(board, metadata, [], None, layout,
                           faded_squares=faded)
        time.sleep(delay)

    return False


# ---------------------------------------------------------------------------
# Fade effect
# ---------------------------------------------------------------------------

def _fade_board(stdscr, renderer, board, metadata, move_log, layout, result_display):
    """
    Progressively clear pieces from the board over ~1 second.
    Returns True if the user pressed a key.
    """
    occupied = [sq for sq in chess.SQUARES if board.piece_at(sq) is not None]
    random.shuffle(occupied)

    if not occupied:
        return False

    delay = min(0.05, 1.0 / len(occupied))
    faded: set[int] = set()

    for sq in occupied:
        if _check_quit(stdscr):
            return True
        faded.add(sq)
        renderer.draw_full(board, metadata, move_log, None, layout,
                           result_display=result_display,
                           faded_squares=faded)
        time.sleep(delay)

    return False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_metadata(game):
    h = game.headers
    return {
        'white':        h.get('White',        '?'),
        'black':        h.get('Black',        '?'),
        'white_elo':    h.get('WhiteElo',     ''),
        'black_elo':    h.get('BlackElo',     ''),
        'opening':      h.get('Opening',      h.get('ECOName', '')),
        'time_control': h.get('TimeControl',  ''),
        'date':         h.get('Date',         '?'),
        'result':       h.get('Result',       '*'),
    }


def _format_result(result):
    if result == '1-0':
        return ('★ 1-0  White wins ★', 'win')
    if result == '0-1':
        return ('★ 0-1  Black wins ★', 'loss')
    if result == '1/2-1/2':
        return ('★ ½-½  Draw ★',        'draw')
    return (f'★ {result} ★',            'draw')


def _check_quit(stdscr):
    """Return True if any key has been pressed."""
    return stdscr.getch() != -1


def _timed_wait(stdscr, seconds):
    """
    Wait for `seconds`, checking for keypresses every 20 ms.
    Returns True if a key was pressed (caller should quit).
    """
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if stdscr.getch() != -1:
            return True
        time.sleep(0.02)
    return False
