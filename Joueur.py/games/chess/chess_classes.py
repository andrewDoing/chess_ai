from enum import Enum

# Data structures for chess

########## CONSTANTS ##########
# Forsyth-Edwards Notation
B_PAWN   = "p"
B_KNIGHT = "n"
B_BISHOP = "b"
B_ROOK   = "r"
B_QUEEN  = "q"
B_KING   = "k"
BLACK_PIECES = {B_PAWN, B_KNIGHT, B_BISHOP, B_ROOK, B_QUEEN, B_KING}
BLACK_PROMO = (B_KNIGHT, B_BISHOP, B_ROOK, B_QUEEN)

W_PAWN = "P"
W_KNIGHT = "N"
W_BISHOP = "B"
W_ROOK = "R"
W_QUEEN = "Q"
W_KING = "K"
WHITE_PIECES = {W_PAWN, W_KNIGHT, W_BISHOP, W_ROOK, W_QUEEN, W_KING}
WHITE_PROMO = (W_KNIGHT, W_BISHOP, W_ROOK, W_QUEEN)

PIECES = WHITE_PIECES.union(BLACK_PIECES)

# Material Advantage Constants
MA_PAWN = 1
MA_KNIGHT = 3
MA_BISHOP = 3
MA_ROOK = 5
MA_QUEEN = 9
MA_KING = 999

WHITE_ACTIVE = "w"
BLACK_ACTIVE = "b"
CASTLE_KINGSIDE = "O-O"
CASTLE_QUEENSIDE = "O-O-O"

# Set of Pieces
PAWN_SET = {B_PAWN, W_PAWN}
KNIGHT_SET = {B_KNIGHT, W_KNIGHT}
BISHOP_SET = {B_BISHOP, W_BISHOP}
ROOK_SET = {B_ROOK, W_ROOK}
QUEEN_SET = {B_QUEEN, W_QUEEN}
KING_SET = {B_KING, W_KING}

# Map the pieces based on color
PAWN_MAP = {BLACK_ACTIVE:B_PAWN, WHITE_ACTIVE:W_PAWN}
KNIGHT_MAP = {BLACK_ACTIVE:B_KNIGHT, WHITE_ACTIVE:W_KNIGHT}
BISHOP_MAP = {BLACK_ACTIVE:B_BISHOP, WHITE_ACTIVE:W_BISHOP}
ROOK_MAP = {BLACK_ACTIVE:B_ROOK, WHITE_ACTIVE:W_ROOK}
QUEEN_MAP = {BLACK_ACTIVE:B_QUEEN, WHITE_ACTIVE:W_QUEEN}
KING_MAP = {BLACK_ACTIVE:B_KING, WHITE_ACTIVE:W_KING}

# Mapping the traditional chess ranks to their numpy array indeces
RANK_1 = FILE_H = MAX_POS = 7
RANK_2 = FILE_G           = 6
RANK_3 = FILE_F           = 5
RANK_4 = FILE_E           = 4
RANK_5 = FILE_D           = 3
RANK_6 = FILE_C           = 2
RANK_7 = FILE_B           = 1
RANK_8 = FILE_A = MIN_POS = 0
VALID_RANKS = {RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8}

# Algebraic representations
A_RANK_1 = "1"
A_RANK_2 = "2"
A_RANK_3 = "3"
A_RANK_4 = "4"
A_RANK_5 = "5"
A_RANK_6 = "6"
A_RANK_7 = "7"
A_RANK_8 = "8"
A_FILE_A = "a"
A_FILE_B = "b"
A_FILE_C = "c"
A_FILE_D = "d"
A_FILE_E = "e"
A_FILE_F = "f"
A_FILE_G = "g"
A_FILE_H = "h"

NO_PIECE = " " # No piece on this square
NO_C_EP = "-" # No castle or en passant

# Movement Vectors
V_UP           = (-1, 0)
V_UP_2         = (-2, 0)
V_DOWN         = (1, 0)
V_DOWN_2       = (2, 0)
V_LEFT         = (0, -1)
V_RIGHT        = (0, 1)
V_UP_LEFT      = (-1, -1)
V_UP_RIGHT     = (-1, 1)
V_DOWN_LEFT    = (1, -1)
V_DOWN_RIGHT   = (1, 1)
V_EIGHT_OCLOCK = (1, -2) 
V_SEV_OCLOCK   = (2, -1)
V_FIVE_OCLOCK  = (2, 1)
V_FOUR_OCLOCK  = (1, 2)
V_TWO_OCLOCK   = (-1, 2)
V_ONE_OCLOCK   = (-2, 1)
V_EL_OCLOCK    = (-2, -1)
V_TEN_OCLOCK   = (-1, -2)

# Possible Single Square Moves for the pieces
W_PAWN_CAPTURE_VECTORS = (V_UP_LEFT, V_UP_RIGHT)
B_PAWN_CAPTURE_VECTORS = (V_DOWN_LEFT, V_DOWN_RIGHT)
KNIGHT_VECTORS = (V_EIGHT_OCLOCK, V_SEV_OCLOCK, V_FIVE_OCLOCK, V_FOUR_OCLOCK, V_TWO_OCLOCK, V_ONE_OCLOCK, V_EL_OCLOCK, V_TEN_OCLOCK)
BISHOP_VECTORS = (V_UP_LEFT, V_UP_RIGHT, V_DOWN_LEFT, V_DOWN_RIGHT)
ROOK_VECTORS = (V_UP, V_DOWN, V_LEFT, V_RIGHT)
QUEEN_VECTORS = (BISHOP_VECTORS + ROOK_VECTORS)
KING_VECTORS = QUEEN_VECTORS
# Sets of Vectors
BISHOP_VECTOR_SET = {V_UP_LEFT, V_UP_RIGHT, V_DOWN_LEFT, V_DOWN_RIGHT}
ROOK_VECTOR_SET = {V_UP, V_DOWN, V_LEFT, V_RIGHT}
QUEEN_VECTOR_SET = BISHOP_VECTOR_SET | ROOK_VECTOR_SET
KING_VECTOR_SET = QUEEN_VECTOR_SET


# Class definitions for Chess
class GameState:
    """Contains all the information needed for a state of chess"""
    __slots__ = ['board', 'active_color',  'opp_color', 'castles_avail', 'en_passant', 'halfmove', 'fullmove', 'active_king', 'inactive_king', 'history']
    def __init__(self, board, active_color, castles_avail, en_passant, halfmove, fullmove, active_king=None, inactive_king=None, history=None):
        self.board         = board                      # 2D Numpy array of characters
        self.active_color  = active_color               # Who's moving next?
        self.opp_color     = self.get_opp_color()       # Who's the enemy?
        self.castles_avail = castles_avail              # Who can castle still?
        self.en_passant    = alg_to_coord(en_passant)   # Square behind a pawn that just moved 2. (rank, file)
        self.halfmove      = int(halfmove)              # Moves since last capture or pawn advance
        self.fullmove      = int(fullmove)              # Number of full move. Incremented after black moves
        self.active_king   = self.find_king(self.active_color) # Active King Location
        self.inactive_king = self.find_king(self.opp_color) # Inactive King Location
        self.history       = history                    # Needs to be manually set in the AI File

    def get_pieces(self, color):
        if color == WHITE_ACTIVE:
            piece_set = WHITE_PIECES
        elif color == BLACK_ACTIVE:
            piece_set = BLACK_PIECES

        pieces = {}
        for rank in range(8):
            for column in range(8):
                piece = self.board[rank, column]
                if piece in piece_set:
                    if piece in pieces:
                        pieces[piece] += 1
                    else:
                        pieces[piece] = 1
        return pieces
    
    def get_opp_color(self):
        if self.active_color == WHITE_ACTIVE:
            opp_color = BLACK_ACTIVE
        else:
            opp_color = WHITE_ACTIVE
        return opp_color

    def find_king(self, color):
        if color == WHITE_ACTIVE:
            for rank in range(7, -1, -1):
                for column in range(8):
                    if self.board[rank, column] == W_KING:
                        return (rank, column)
        elif color == BLACK_ACTIVE:
            for rank in range(8):
                for column in range(8):
                    if self.board[rank, column] == B_KING:
                        return (rank, column)
        else:
            raise Exception("find_king: Invalid King Color")

    def get_fen(self):
        """Returns FEN string that represents the current state."""
        fen_string = ""

        # Iterate over the board
        for rank in range(8):
            blank_count = 0
            for column in range(8):
                if self.board[rank, column] in BLACK_PIECES:
                    if blank_count != 0:
                        fen_string += str(blank_count)
                    # Reset blank count
                    blank_count = 0
                    if self.board[rank, column] == B_PAWN:
                        fen_string += B_PAWN
                    elif self.board[rank, column] == B_KNIGHT:
                        fen_string += B_KNIGHT
                    elif self.board[rank, column] == B_BISHOP:
                        fen_string += B_BISHOP
                    elif self.board[rank, column] == B_ROOK:
                        fen_string += B_ROOK
                    elif self.board[rank, column] == B_QUEEN:
                        fen_string += B_QUEEN
                    elif self.board[rank, column] == B_KING:
                        fen_string += B_KING
                elif self.board[rank, column] in WHITE_PIECES:
                    if blank_count != 0:
                        fen_string += str(blank_count)
                    # Reset blank count
                    blank_count = 0
                    if self.board[rank, column] == W_PAWN:
                        fen_string += W_PAWN
                    elif self.board[rank, column] == W_KNIGHT:
                        fen_string += W_KNIGHT
                    elif self.board[rank, column] == W_BISHOP:
                        fen_string += W_BISHOP
                    elif self.board[rank, column] == W_ROOK:
                        fen_string += W_ROOK
                    elif self.board[rank, column] == W_QUEEN:
                        fen_string += W_QUEEN
                    elif self.board[rank, column] == W_KING:
                        fen_string += W_KING
                else: # Blank space
                    blank_count += 1
            # Append blank count if there is one
            if blank_count != 0:
                fen_string += str(blank_count)
            # Don't append a slash at the end of the board
            if rank != RANK_1:
                fen_string += "/"

        # Fix issue where en_passant can be a coord or "-"
        if self.en_passant is tuple:
            en_p_alg = coord_to_alg(self.en_passant)
        else:
            en_p_alg = self.en_passant

        # Finished with board, next is the rest
        fen_string += " {} {} {} {} {}".format(
            self.active_color,
            self.castles_avail,
            en_p_alg,
            str(self.halfmove),
            str(self.fullmove)
            )
        return fen_string

class Action: # Lawsuit
    """Players make Actions that are used to update the GameState"""
    __slots__ = ['piece', 'start', 'end', 'capture', 'en_p', 'castle', 'promo']
    def __init__(self, piece=None, start=None, end=None, capture=False, en_p=None, castle=None, promo=None):
        self.piece = piece      # Piece that is moving
        self.start = start      # (rank, file)
        self.end = end          # (rank, file)
        self.capture = capture  # True or False
        self.en_p = en_p        # Space where pawn can be en passant attacked
        self.castle = castle    # SAN for Castling
        self.promo = promo      # Piece to promote the pawn to

    def __repr__(self):
        return "({0}, {1}, {2}, {3}, {4}, {5}, {6})\n".format(self.piece, self.start, self.end, self.capture, self.en_p, self.castle, self.promo)

# Functions
def coord_to_alg(coord):
    """Turns a numerical coordinate tuple into the algebraic rank/file notation"""
    # Ensure the coordinates are on the board
    if coord:
        if coord[0] > MAX_POS or coord[0] < MIN_POS:
            raise Exception("coord_to_alg: Rank off the board: {}".format(coord))
        elif coord[1] > MAX_POS or coord[1] < MIN_POS:
            raise Exception("coord_to_alg: File off the board: {}".format(coord))
        else:
            # Files
            if coord[1] == FILE_A:
                alg = A_FILE_A
            elif coord[1] == FILE_B:
                alg = A_FILE_B
            elif coord[1] == FILE_C:
                alg = A_FILE_C
            elif coord[1] == FILE_D:
                alg = A_FILE_D
            elif coord[1] == FILE_E:
                alg = A_FILE_E
            elif coord[1] == FILE_F:
                alg = A_FILE_F
            elif coord[1] == FILE_G:
                alg = A_FILE_G
            elif coord[1] == FILE_H:
                alg = A_FILE_H
            # Ranks
            if coord[0] == RANK_1:
                alg += A_RANK_1
            elif coord[0] == RANK_2:
                alg += A_RANK_2 
            elif coord[0] == RANK_3:
                alg += A_RANK_3
            elif coord[0] == RANK_4:
                alg += A_RANK_4
            elif coord[0] == RANK_5:
                alg += A_RANK_5
            elif coord[0] == RANK_6:
                alg += A_RANK_6
            elif coord[0] == RANK_7:
                alg += A_RANK_7
            elif coord[0] == RANK_8:
                alg += A_RANK_8
    else:
        alg = NO_C_EP
    return alg

def alg_to_coord(alg):
    """Returns the tuple equivalent to the algebraic position. Must be 2 characters"""
    rank = None
    column = None 
    if alg:
        if len(alg) == 2:
            # Files
            if alg[0] == A_FILE_A:
                column = FILE_A
            elif alg[0] == A_FILE_B:
                column = FILE_B
            elif alg[0] == A_FILE_C:
                column = FILE_C
            elif alg[0] == A_FILE_D:
                column = FILE_D
            elif alg[0] == A_FILE_E:
                column = FILE_E
            elif alg[0] == A_FILE_F:
                column = FILE_F
            elif alg[0] == A_FILE_G:
                column = FILE_G
            elif alg[0] == A_FILE_H:
                column = FILE_H
            else:
                raise Exception("alg_to_coord: Invalid File")
            # Ranks
            if alg[1] == A_RANK_1:
                rank = RANK_1
            elif alg[1] == A_RANK_2:
                rank = RANK_2
            elif alg[1] == A_RANK_3:
                rank = RANK_3
            elif alg[1] == A_RANK_4:
                rank = RANK_4
            elif alg[1] == A_RANK_5:
                rank = RANK_5
            elif alg[1] == A_RANK_6:
                rank = RANK_6
            elif alg[1] == A_RANK_7:
                rank = RANK_7
            elif alg[1] == A_RANK_8:
                rank = RANK_8
            else:
                raise Exception("alg_to_coord: Invalid Rank")
            return (rank, column)
        elif alg == NO_C_EP:
            return None
        else:
            raise Exception("alg_to_coord: alg longer than 2")
    else:
        return None

