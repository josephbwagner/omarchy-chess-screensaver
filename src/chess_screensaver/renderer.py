import curses

import chess

from .board import (
    DARK_SQUARE, LIGHT_SQUARE,
    get_piece_symbol, is_light_square,
)

# Color pair IDs
CP_DEFAULT     = 1   # default foreground on default background
CP_DIM         = 2   # color 8 (bright-black / dim)
CP_LABEL       = 3   # color 6 (cyan) — info labels
CP_VALUE       = 4   # color 7 (white) — info values
CP_ACCENT      = 5   # color 3 (yellow) — active move / highlight brackets
CP_WHITE_PIECE = 6   # color 15 (bright white) — white pieces
CP_BLACK_PIECE = 7   # color 8 (dim) — black pieces
CP_GREEN       = 8   # color 2 (green) — win result
CP_RED         = 9   # color 1 (red) — loss result


def _init_colors():
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(CP_DEFAULT, 7, -1)
    curses.init_pair(CP_LABEL,   6, -1)
    curses.init_pair(CP_VALUE,   7, -1)
    curses.init_pair(CP_ACCENT,  3, -1)
    curses.init_pair(CP_GREEN,   2, -1)
    curses.init_pair(CP_RED,     1, -1)

    if curses.COLORS >= 16:
        curses.init_pair(CP_DIM,         8, -1)
        curses.init_pair(CP_WHITE_PIECE, 15, -1)
        curses.init_pair(CP_BLACK_PIECE,  8, -1)
    else:
        # Fallback for 8-color terminals
        curses.init_pair(CP_DIM,         0, -1)
        curses.init_pair(CP_WHITE_PIECE, 7, -1)
        curses.init_pair(CP_BLACK_PIECE, 0, -1)


def _format_time_control(tc):
    """Convert a Lichess TimeControl value like '180+0' to '3+0 (Blitz)'."""
    if not tc or tc in ('?', '-'):
        return '?'
    # Handle bare seconds with no increment
    if '+' not in tc and tc.isdigit():
        tc = tc + '+0'
    parts = tc.split('+')
    if len(parts) == 2:
        try:
            secs = int(parts[0])
            incr = int(parts[1])
            mins = secs // 60
            if secs < 30:
                label = 'UltraBullet'
            elif mins < 3:
                label = 'Bullet'
            elif mins < 8:
                label = 'Blitz'
            elif mins < 25:
                label = 'Rapid'
            else:
                label = 'Classical'
            return f'{mins}+{incr} ({label})'
        except ValueError:
            pass
    return tc


class Renderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        _init_colors()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def draw_full(self, board, metadata, move_log, highlight, layout,
                  result_display=None, faded_squares=None):
        """Redraw the entire screen from scratch."""
        scr = self.stdscr
        scr.erase()

        lines = layout['lines']
        cols  = layout['cols']

        if lines < 13 or cols < 60:
            msg = 'Terminal too small — please resize'
            self._safe_addstr(lines // 2, max(0, (cols - len(msg)) // 2),
                              msg, curses.color_pair(CP_DEFAULT))
            scr.refresh()
            return

        self._draw_border(layout)
        self._draw_divider(layout)
        self._draw_board(board, highlight, faded_squares, layout)
        self._draw_info(metadata, move_log, result_display, layout)
        scr.refresh()

    # ------------------------------------------------------------------
    # Border & divider
    # ------------------------------------------------------------------

    def _draw_border(self, layout):
        lines = layout['lines']
        cols  = layout['cols']
        attr  = curses.color_pair(CP_DIM)

        self._safe_addstr(0, 0, '┌', attr)
        self._safe_addstr(0, 1, '─' * (cols - 2), attr)
        self._safe_addstr(0, cols - 1, '┐', attr)

        self._safe_addstr(lines - 1, 0, '└', attr)
        self._safe_addstr(lines - 1, 1, '─' * (cols - 2), attr)
        self._safe_addstr(lines - 1, cols - 1, '┘', attr)

        for y in range(1, lines - 1):
            self._safe_addstr(y, 0,        '│', attr)
            self._safe_addstr(y, cols - 1, '│', attr)

    def _draw_divider(self, layout):
        lines     = layout['lines']
        divider_x = layout['divider_x']
        attr      = curses.color_pair(CP_DIM)
        for y in range(1, lines - 1):
            self._safe_addstr(y, divider_x, '│', attr)

    # ------------------------------------------------------------------
    # Chess board
    # ------------------------------------------------------------------

    def _draw_board(self, board, highlight, faded_squares, layout):
        board_x = layout['board_x']
        board_y = layout['board_y']
        faded   = faded_squares or set()

        hl_from = highlight[0] if highlight else None
        hl_to   = highlight[1] if highlight else None

        for rank in range(7, -1, -1):
            y = board_y + (7 - rank)

            # Rank label ("8 ", "7 ", …)
            self._safe_addstr(y, board_x, f'{rank + 1} ', curses.color_pair(CP_DIM))

            for file in range(8):
                sq = chess.square(file, rank)
                x  = board_x + 2 + file * 4  # 2 chars for rank label

                light      = is_light_square(sq)
                is_faded   = sq in faded
                is_hl      = sq == hl_from or sq == hl_to
                piece      = None if is_faded else board.piece_at(sq)

                if piece is None:
                    char = LIGHT_SQUARE if light else DARK_SQUARE
                    if is_hl:
                        attr = curses.color_pair(CP_ACCENT)
                    elif light:
                        attr = curses.color_pair(CP_DEFAULT)
                    else:
                        attr = curses.color_pair(CP_DIM)
                else:
                    char = get_piece_symbol(piece)
                    if is_hl:
                        attr = curses.color_pair(CP_ACCENT)
                    elif piece.color == chess.WHITE:
                        attr = curses.color_pair(CP_WHITE_PIECE)
                        if curses.COLORS < 16:
                            attr |= curses.A_BOLD
                    else:
                        attr = curses.color_pair(CP_BLACK_PIECE)

                cell = f'[{char}] ' if is_hl else f' {char}  '
                self._safe_addstr(y, x, cell, attr)

        # File labels: "   a   b   c   d   e   f   g   h"
        file_row = '  ' + ''.join(f' {chr(ord("a") + f)}  ' for f in range(8))
        self._safe_addstr(board_y + 8, board_x, file_row, curses.color_pair(CP_DIM))

    # ------------------------------------------------------------------
    # Info panel
    # ------------------------------------------------------------------

    def _draw_info(self, metadata, move_log, result_display, layout):
        info_x   = layout['info_start_x']
        info_w   = layout['info_panel_width']
        lines    = layout['lines']

        y = 1  # start at top of interior

        def write(text, attr=None):
            if attr is None:
                attr = curses.color_pair(CP_VALUE)
            truncated = (' ' + text)[:info_w]
            self._safe_addstr(y, info_x, truncated, attr)

        def divider():
            d = ' ' + '─' * min(info_w - 2, 26)
            self._safe_addstr(y, info_x, d, curses.color_pair(CP_DIM))

        # ── MATCH INFO header ──────────────────────────────────────────
        write('MATCH INFO', curses.color_pair(CP_LABEL))
        y += 1
        divider()
        y += 1

        # White player
        white     = metadata.get('white', '?')
        white_elo = metadata.get('white_elo', '')
        w_str     = f'{white} ({white_elo})' if white_elo and white_elo not in ('?', '') else white
        self._write_kv('White: ', w_str, y, info_x, info_w)
        y += 1

        # Black player
        black     = metadata.get('black', '?')
        black_elo = metadata.get('black_elo', '')
        b_str     = f'{black} ({black_elo})' if black_elo and black_elo not in ('?', '') else black
        self._write_kv('Black: ', b_str, y, info_x, info_w)
        y += 1

        y += 1  # blank line

        # Opening (may be long — wrap up to 2 lines)
        opening = metadata.get('opening', '')
        if opening:
            y += self._draw_wrapped_kv('Opening: ', opening, y, info_x, info_w)

        # Time control
        tc = _format_time_control(metadata.get('time_control', ''))
        self._write_kv('Time: ', tc, y, info_x, info_w)
        y += 1

        # Date
        self._write_kv('Date: ', metadata.get('date', '?'), y, info_x, info_w)
        y += 1

        # Result
        if result_display:
            text, rtype = result_display
            if rtype == 'win':
                attr = curses.color_pair(CP_GREEN)
            elif rtype == 'loss':
                attr = curses.color_pair(CP_RED)
            else:
                attr = curses.color_pair(CP_ACCENT)
            self._safe_addstr(y, info_x, (' ' + text)[:info_w], attr)
        else:
            self._write_kv('Result: ', metadata.get('result', '?'), y, info_x, info_w)
        y += 1

        y += 1  # blank line

        # ── MOVES header ───────────────────────────────────────────────
        if y >= lines - 2:
            return
        write('MOVES', curses.color_pair(CP_LABEL))
        y += 1
        if y >= lines - 2:
            return
        divider()
        y += 1

        # ── Move log ───────────────────────────────────────────────────
        moves_area_top    = y
        moves_area_height = (lines - 1) - moves_area_top  # line before bottom border

        if moves_area_height <= 0 or not move_log:
            return

        # Show only the last N moves that fit
        visible     = move_log[-moves_area_height:]
        active_idx  = len(move_log) - 1  # index of the last (active) pair

        for i, entry in enumerate(visible):
            log_y = moves_area_top + i
            if log_y >= lines - 1:
                break

            num       = entry[0]
            white_san = entry[1] if len(entry) > 1 else ''
            black_san = entry[2] if len(entry) > 2 else ''

            line = f' {num:>3}. {white_san:<7} {black_san:<7}'
            line = line[:info_w]

            actual_idx = (len(move_log) - len(visible)) + i
            attr = (curses.color_pair(CP_ACCENT)
                    if actual_idx == active_idx
                    else curses.color_pair(CP_VALUE))

            self._safe_addstr(log_y, info_x, line, attr)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _write_kv(self, label, value, y, info_x, info_w):
        """Write a label (cyan) + value (white) pair, truncating to info_w."""
        label_attr = curses.color_pair(CP_LABEL)
        value_attr = curses.color_pair(CP_VALUE)

        text = ' ' + label + value
        if len(text) > info_w:
            text = text[:info_w]

        label_part = (' ' + label)[:info_w]
        value_part = text[len(label_part):]

        self._safe_addstr(y, info_x, label_part, label_attr)
        if value_part:
            self._safe_addstr(y, info_x + len(label_part), value_part, value_attr)

    def _draw_wrapped_kv(self, label, value, y, info_x, info_w, max_lines=2):
        """
        Like _write_kv but wraps the value across up to max_lines lines.
        Returns the number of lines consumed.
        """
        label_attr = curses.color_pair(CP_LABEL)
        value_attr = curses.color_pair(CP_VALUE)

        label_part  = (' ' + label)[:info_w]
        first_avail = max(0, info_w - len(label_part))
        indent      = len(label_part)

        # First line: label + as much value as fits
        self._safe_addstr(y, info_x, label_part, label_attr)
        if first_avail > 0:
            self._safe_addstr(y, info_x + indent, value[:first_avail], value_attr)

        remainder  = value[first_avail:]
        lines_used = 1

        # Continuation lines indented to align with value column
        cont_avail = max(0, info_w - indent)
        while remainder and lines_used < max_lines and cont_avail > 0:
            part      = remainder[:cont_avail]
            remainder = remainder[cont_avail:]
            self._safe_addstr(y + lines_used, info_x + indent, part, value_attr)
            lines_used += 1

        return lines_used

    def _safe_addstr(self, y, x, text, attr=0):
        try:
            self.stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass
