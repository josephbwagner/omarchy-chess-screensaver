import io
import os
import random

import chess.pgn


def get_pgn_files(data_dir):
    """Return list of .pgn file paths in data_dir/pgn/."""
    pgn_dir = os.path.join(data_dir, 'pgn')
    try:
        names = [f for f in os.listdir(pgn_dir) if f.lower().endswith('.pgn')]
        return [os.path.join(pgn_dir, n) for n in sorted(names)]
    except OSError:
        return []


def load_random_game(data_dir):
    """
    Select a random PGN file from data_dir/pgn/, seek to a random position,
    find the next game header, and parse the game.  Returns a chess.pgn.Game
    or None if no valid game could be found.
    """
    pgn_files = get_pgn_files(data_dir)
    if not pgn_files:
        return None

    # Shuffle so we don't keep retrying the same bad file
    candidates = list(pgn_files)
    random.shuffle(candidates)

    for filepath in candidates:
        game = _load_game_from_file(filepath)
        if game is not None:
            return game

    return None


def _load_game_from_file(filepath):
    """
    Seek to a random byte offset in the file, scan forward to the next
    [Event header, and parse the game with python-chess.
    """
    try:
        size = os.path.getsize(filepath)
        if size == 0:
            return None

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            offset = random.randint(0, max(0, size - 1))
            f.seek(offset)
            rest = f.read()

            # Look for a game header after our seek position
            idx = rest.find('\n[Event ')
            if idx != -1:
                game_text = rest[idx + 1:]  # skip the leading newline
            else:
                # Wrap around: try from the start of the file
                f.seek(0)
                game_text = f.read()
                idx = game_text.find('[Event ')
                if idx == -1:
                    return None
                game_text = game_text[idx:]

            game = chess.pgn.read_game(io.StringIO(game_text))
            if game is None:
                return None

            # Require at least one legal move
            if game.next() is None:
                return None

            return game

    except Exception:
        return None
