import numpy as np

from games.chess.chess_classes import W_PAWN, W_KNIGHT, W_BISHOP, W_ROOK, W_QUEEN, W_KING, WHITE_PIECES
from games.chess.chess_classes import B_PAWN, B_KNIGHT, B_BISHOP, B_ROOK, B_QUEEN, B_KING, BLACK_PIECES
from games.chess.chess_classes import PIECES, MA_PAWN
from games.chess.chess_classes import RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8
from games.chess.chess_classes import FILE_A, FILE_B, FILE_C, FILE_D, FILE_E, FILE_F, FILE_G, FILE_H
from games.chess.chess_classes import MAX_POS, MIN_POS, VALID_RANKS
from games.chess.chess_classes import CASTLE_KINGSIDE, CASTLE_QUEENSIDE
from games.chess.chess_classes import GameState, Action
from games.chess.chess_classes import coord_to_alg
from games.chess.chess_classes import alg_to_coord


def fen_to_GameState(fen):
    """Takes fen string and returns the numpy array reflecting it.
    """
    # split the FEN string up to help parse it
    split = fen.split(' ')
    first = split[0]  # the first part is always the board locations
    lines = first.split('/') # get each line of the board
    board_2d_list = []

    for line in (lines):
        rank_list = []
        for char in line:
            try:
                char_as_number = int(char)
                # it is a number, so that many blank spaces
                for _ in range(char_as_number):
                    rank_list.append(' ')
            except:
                rank_list.append(char)
        board_2d_list.append(rank_list)

    dt = np.dtype(np.unicode_, 1) # Datatype for the numpy array
    board = np.array(board_2d_list, dtype=dt) # Generate the numpy array

    active = split[1] # Get the active color
    castles = split[2] # Get the available castles
    en_passant = split[3] # Get the available en passant capture
    halfmove = (split[4])
    fullmove = split[5]

    return GameState(board, active, castles, en_passant, halfmove, fullmove)

def san(action):
    """ Returns SAN that represents the action.
        Action format for my code:
            (Piece, Starting Square, Ending Square, Capture?, Castle, En Passant, Promote Pawn)
    """
    san = ""
    if action.castle == CASTLE_KINGSIDE:
        san = "O-O"
    elif action.castle == CASTLE_QUEENSIDE:
        san = "O-O-O"
    else:
        # Standard Moves
        if action.piece == W_PAWN or action.piece == B_PAWN:
            san = san # No letter
        elif action.piece in BLACK_PIECES:
            # Use the white piece letters instead
            if action.piece == B_KNIGHT:
                san = W_KNIGHT
            elif action.piece == B_BISHOP:
                san = W_BISHOP
            elif action.piece == B_ROOK:
                san = W_ROOK
            elif action.piece == B_QUEEN:
                san = W_QUEEN
            elif action.piece == B_KING:
                san = W_KING
            else:
                raise Exception("SAN: idk bro lol")
        else:
            san = action.piece
            
        # Append the starting position
        san += coord_to_alg(action.start)
        # Append the capture
        if action.capture:
            san += "x"
        # Append the ending position
        san += coord_to_alg(action.end)
    return san

# def san_to_action(san):
#     """Returns the action tuple from the given SAN
#     """
#     if san == CASTLE_KINGSIDE:
#         castle = CASTLE_KINGSIDE
#         return Action(castle=castle)
#     elif san == CASTLE_QUEENSIDE:
#         castle = CASTLE_QUEENSIDE
#         return Action(castle=castle)
#     else:
#         arr = list(san)

#         # Get the piece making the move
#         if arr[0] in PIECES and arr[1] not in VALID_RANKS:
#             piece = arr[0]
#             start_alg = arr[1]+arr[2]
#             start = alg_to_coord(start_alg)
#             # Is it a capture?
#             if arr[3] == "x":
#                 capture = True
#                 end_alg = arr[4]+arr[5]
#                 end = alg_to_coord(end_alg)
#             else:
#                 capture = False
#                 end_alg = arr[3]+arr[4]
#                 end = alg_to_coord(end_alg)
#         else:
#             piece = MA_PAWN
#             start_alg = arr[0]+arr[1]
#             start = alg_to_coord(start_alg)
#             # Is it a capture?
#             if arr[2] == "x":
#                 capture = True
#                 end_alg = arr[3]+arr[4]
#                 end = alg_to_coord(end_alg)
#             else:
#                 capture = False
#                 end_alg = arr[2]+arr[3]
#                 end = alg_to_coord(end_alg)

#     return Action(piece, start, end, capture)