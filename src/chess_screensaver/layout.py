import math


def calculate_layout(lines, cols):
    """
    Compute panel geometry for the screensaver layout.

    Returns a dict with all positions and dimensions needed for rendering.
    Interior is the area inside the 1-char-thick border.
    """
    interior_lines = lines - 2
    interior_cols = cols - 2

    # Board panel: at least 26 cols wide (2 rank label + 24 board), target 2/3 of interior
    board_panel_width = max(26, math.floor(interior_cols * 2 / 3))

    # Ensure the info panel gets at least 20 chars; clamp board panel if needed
    if board_panel_width > interior_cols - 21:
        board_panel_width = max(26, interior_cols - 21)

    info_panel_width = interior_cols - board_panel_width - 1  # -1 for divider

    divider_x = 1 + board_panel_width
    info_start_x = divider_x + 1

    # Board content dimensions: 26 wide (2 rank label + 8×3 squares), 9 tall (8 ranks + file row)
    board_content_w = 26
    board_content_h = 9

    # Center board within board panel and interior height
    board_x = 1 + max(0, (board_panel_width - board_content_w) // 2)
    board_y = 1 + max(0, (interior_lines - board_content_h) // 2)

    return {
        'lines': lines,
        'cols': cols,
        'interior_lines': interior_lines,
        'interior_cols': interior_cols,
        'board_panel_width': board_panel_width,
        'info_panel_width': info_panel_width,
        'divider_x': divider_x,
        'info_start_x': info_start_x,
        'board_x': board_x,
        'board_y': board_y,
    }
