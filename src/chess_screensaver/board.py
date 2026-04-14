import chess

# Unicode piece symbols
WHITE_PIECES = {
    chess.KING:   '♔',
    chess.QUEEN:  '♕',
    chess.ROOK:   '♖',
    chess.BISHOP: '♗',
    chess.KNIGHT: '♘',
    chess.PAWN:   '♙',
}

BLACK_PIECES = {
    chess.KING:   '♚',
    chess.QUEEN:  '♛',
    chess.ROOK:   '♜',
    chess.BISHOP: '♝',
    chess.KNIGHT: '♞',
    chess.PAWN:   '♟',
}

LIGHT_SQUARE = '·'  # U+00B7 middle dot
DARK_SQUARE  = '░'  # U+2591 light shade block


def is_light_square(sq):
    """Return True if square is a light square (file + rank sum is odd)."""
    return (chess.square_file(sq) + chess.square_rank(sq)) % 2 == 1


def get_piece_symbol(piece):
    """Return the Unicode symbol for a chess piece."""
    if piece.color == chess.WHITE:
        return WHITE_PIECES[piece.piece_type]
    return BLACK_PIECES[piece.piece_type]
