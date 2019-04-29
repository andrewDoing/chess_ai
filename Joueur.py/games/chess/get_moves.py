from games.chess import chess_classes as cc
from games.chess import check

class Piece:
    """Each Piece on the board"""
    __slots__ = ['string', 'coord', 'color']
    def __init__(self, string, coord):
        self.string = string
        self.coord = coord

        if self.string in cc.BLACK_PIECES:
            self.color = cc.BLACK_ACTIVE
        elif string in cc.WHITE_PIECES:
            self.color = cc.WHITE_ACTIVE
        else:
            self.color = None
            raise Exception('Piece.__init__: Invalid Color')

    def get_moves(self, state):
        possible_moves = []
        if self.string in cc.PAWN_SET:
            possible_moves = self.get_pawn_moves(state)
        elif self.string in cc.KNIGHT_SET:
            possible_moves = self.get_knight_moves(state)
        elif self.string in cc.BISHOP_SET:
            possible_moves = get_bishop_moves(state, self.coord)
        elif self.string in cc.ROOK_SET:
            possible_moves = get_rook_moves(state, self.coord)
        elif self.string in cc.QUEEN_SET:
            possible_moves = get_queen_moves(state, self.coord)
        elif self.string in cc.KING_SET:
            possible_moves = self.get_king_moves(state)
        return tuple(possible_moves)

    def get_pawn_moves(self, state):
        """Returns the moves for the pawn at the given location
        """
        pawn_moves = []

        if self.color == cc.WHITE_ACTIVE:
            forward_1 = add_vectors(self.coord, cc.V_UP)
            forward_2 = add_vectors(self.coord, cc.V_UP_2)
            attacks = get_crawler_moves(self.coord, cc.W_PAWN_CAPTURE_VECTORS)
            starting_rank = cc.RANK_2
            promo_rank = cc.RANK_8
            promo_pieces = cc.WHITE_PROMO
            enemy_set = cc.BLACK_PIECES
        elif self.color == cc.BLACK_ACTIVE:
            forward_1 = add_vectors(self.coord, cc.V_DOWN)
            forward_2 = add_vectors(self.coord, cc.V_DOWN_2)
            attacks = get_crawler_moves(self.coord, cc.B_PAWN_CAPTURE_VECTORS)
            starting_rank = cc.RANK_7
            promo_rank = cc.RANK_1
            promo_pieces = cc.BLACK_PROMO
            enemy_set = cc.WHITE_PIECES
        else:
            raise Exception("get_pawn_moves: Invalid Piece Color")

        if validate_move(forward_1) and state.board[forward_1] == cc.NO_PIECE:
            if forward_1[0] == promo_rank:
                for p in promo_pieces:
                    pawn_moves.append(cc.Action(self.string, self.coord, forward_1, promo=p))
            else:
                pawn_moves.append(cc.Action(self.string, self.coord, forward_1))
            if self.coord[0] == starting_rank and validate_move(forward_2) and state.board[forward_2] == cc.NO_PIECE:
                pawn_moves.append(cc.Action(self.string, self.coord, forward_2, en_p=forward_1))

        for attack in attacks:
            if state.board[attack] in enemy_set:
                if attack[0] == promo_rank:
                    for p in promo_pieces:
                        pawn_moves.append(cc.Action(self.string, self.coord, attack, capture=True, promo=p))
                else:
                    pawn_moves.append(cc.Action(self.string, self.coord, attack, capture=True))
            # Make sure Pawns can attack en_passant squares
            elif attack == state.en_passant:
                pawn_moves.append(cc.Action(self.string, self.coord, attack, capture=True))

        return pawn_moves

    def get_knight_moves(self, state):
        """Returns the moves for the knight at the given location
        """
        knight_moves = []
        if self.color == cc.WHITE_ACTIVE:
            enemy_set = cc.BLACK_PIECES
        elif self.color == cc.BLACK_ACTIVE:
            enemy_set = cc.WHITE_PIECES
        else:
            raise Exception("get_knight_moves: Invalid Knight Color")

        possible_moves = get_crawler_moves(self.coord, cc.KNIGHT_VECTORS)
        for move in possible_moves:
            if state.board[move] == cc.NO_PIECE:
                knight_moves.append(cc.Action(self.string, self.coord, move))
            elif state.board[move] in enemy_set:
                knight_moves.append(cc.Action(self.string, self.coord, move, capture=True))

        return knight_moves
    
    def get_king_moves(self, state):
        """Returns the moves for the king at the given location.
        Makes sure that the King doesn't put himself in check.
        """
        #king_moves = []
        possible_moves = []
        if self.color == cc.WHITE_ACTIVE:
            enemy_color = cc.BLACK_ACTIVE
            enemy_pieces = cc.BLACK_PIECES
        elif self.color == cc.BLACK_ACTIVE:
            enemy_color = cc.WHITE_ACTIVE
            enemy_pieces = cc.WHITE_PIECES
        else:
            raise Exception("GameState: Invalid Active Color")

        for vector in cc.KING_VECTORS:
            rank = self.coord[0] + vector[0]
            column = self.coord[1] + vector[1]
            if rank in cc.VALID_RANKS and column in cc.VALID_RANKS:
                if state.board[rank, column] == cc.NO_PIECE:
                    possible_moves.append(cc.Action(self.string, self.coord, (rank, column)))
                elif state.board[rank, column] in enemy_pieces:
                    possible_moves.append(cc.Action(self.string, self.coord, (rank, column), capture=True))
        
        # # Iterate over list of king moves, removing ones that are under attack
        # for move in possible_moves:
        #     if not check.space_under_attack(state, move.end, enemy_color):
        #         king_moves.append(move)

        return possible_moves


def get_castle(state):
        """Returns available castling moves based on the board.
            Return (kingside:T/F, queenside:T/F)
        """
        # TODO: Make sure the castling spaces aren't under attack
        # Queenside: A through E, Kingside: E through H
        q_rook = False
        k_rook = False
        q_space = False
        k_space = False
        king = False

        if state.active_color == cc.WHITE_ACTIVE:
            # Check through rank 1
            rank = cc.RANK_1
            # Check the state to see if castling is available
            wk_avail = True if cc.W_KING in state.castles_avail else False
            wq_avail = True if cc.W_QUEEN in state.castles_avail else False
            if state.board[rank, cc.FILE_E] == cc.W_KING:
                king = True
            if wq_avail:
                if state.board[rank, cc.FILE_A] == cc.W_ROOK:
                    q_rook = True
                if state.board[rank, cc.FILE_B] == cc.NO_PIECE and \
                    state.board[rank, cc.FILE_C] == cc.NO_PIECE and \
                    state.board[rank, cc.FILE_D] == cc.NO_PIECE and \
                    not check.space_under_attack(state, (rank, cc.FILE_B), cc.BLACK_ACTIVE) and \
                    not check.space_under_attack(state, (rank, cc.FILE_C), cc.BLACK_ACTIVE) and \
                    not check.space_under_attack(state, (rank, cc.FILE_D), cc.BLACK_ACTIVE):
                    q_space = True
            if wk_avail:
                if state.board[rank, cc.FILE_F] == cc.NO_PIECE and \
                    state.board[rank, cc.FILE_G] == cc.NO_PIECE and \
                    not check.space_under_attack(state, (rank, cc.FILE_F), cc.BLACK_ACTIVE) and \
                    not check.space_under_attack(state, (rank, cc.FILE_G), cc.BLACK_ACTIVE):
                    k_space = True
                if state.board[rank, cc.FILE_H] == cc.W_ROOK:
                    k_rook = True

            # Check the variables to see what castling is available
            if wk_avail and wq_avail and q_rook and q_space and king and k_space and k_rook:
                return (True, True)
            elif wq_avail and q_rook and q_space and king:
                return (False, True)
            elif wk_avail and king and k_space and k_rook:
                return (True, False)
            else:
                return (False, False)

        elif state.active_color == cc.BLACK_ACTIVE:
            # Loop through rank 8
            rank = cc.RANK_8
            # Check the state to see if castling is available
            bk_avail = True if cc.B_KING in state.castles_avail else False
            bq_avail = True if cc.B_QUEEN in state.castles_avail else False
            if state.board[rank, cc.FILE_E] == cc.B_KING:
                king = True
            if bq_avail:
                if state.board[rank, cc.FILE_A] == cc.B_ROOK:
                    q_rook = True
                if state.board[rank, cc.FILE_B] == cc.NO_PIECE and \
                    state.board[rank, cc.FILE_C] == cc.NO_PIECE and \
                    state.board[rank, cc.FILE_D] == cc.NO_PIECE and \
                    not check.space_under_attack(state, (rank, cc.FILE_B), cc.WHITE_ACTIVE) and \
                    not check.space_under_attack(state, (rank, cc.FILE_C), cc.WHITE_ACTIVE) and \
                    not check.space_under_attack(state, (rank, cc.FILE_D), cc.WHITE_ACTIVE):
                    q_space = True
            if bk_avail:
                if state.board[rank, cc.FILE_F] == cc.NO_PIECE and \
                    state.board[rank, cc.FILE_G] == cc.NO_PIECE and \
                    not check.space_under_attack(state, (rank, cc.FILE_F), cc.WHITE_ACTIVE) and \
                    not check.space_under_attack(state, (rank, cc.FILE_G), cc.WHITE_ACTIVE):
                    k_space = True
                if state.board[rank, cc.FILE_H] == cc.B_ROOK:
                    k_rook = True

            # Check the variables to see what castling is available
            if bk_avail and bq_avail and q_rook and q_space and king and k_space and k_rook:
                return (True, True)
            elif bq_avail and q_rook and q_space and king:
                return (False, True)
            elif bk_avail and king and k_space and k_rook:
                return (True, False)
            else:
                return (False, False)
        else:
            raise Exception("castle_state: Invalid active color")

def get_crawler_moves(coord, vectors):
    """Returns a tuple of possible moves based on the starting position and the vectors.
    Used for Knights, Pawns, and Kings"""
    possible_moves = []
    for vector in vectors:
        try:
            move = (coord[0]+vector[0], coord[1]+vector[1])
        except TypeError as e:
            print("coord: {}".format(coord))
            print("vector: {}".format(vector))
        if move[0] in cc.VALID_RANKS and move[1] in cc.VALID_RANKS:
            possible_moves.append(move)
    return tuple(possible_moves)

def get_direction_moves(state, piece, coord, vector):
    """Loops through the board in the direction specified.
    Returns the moves possible in the direction. 
    Used for Bishops, Rooks, and Queens.
    """
    actions = []
    if state.active_color == cc.WHITE_ACTIVE:
        # Loop
        rank = coord[0] + vector[0]
        column = coord[1] + vector[1]
        while rank in cc.VALID_RANKS and column in cc.VALID_RANKS:
            if state.board[rank, column] == cc.NO_PIECE:
                actions.append(cc.Action(piece, coord, (rank,column)))
            elif state.board[rank, column] in cc.BLACK_PIECES:
                actions.append(cc.Action(piece, coord, (rank,column), capture=True))
                break
            else:
                break
            rank += vector[0]
            column += vector[1]
    elif state.active_color == cc.BLACK_ACTIVE:
        # Loop
        rank = coord[0] + vector[0]
        column = coord[1] + vector[1]
        while rank in cc.VALID_RANKS and column in cc.VALID_RANKS:
            if state.board[rank, column] == cc.NO_PIECE:
                actions.append(cc.Action(piece, coord, (rank,column)))
            elif state.board[rank, column] in cc.WHITE_PIECES:
                actions.append(cc.Action(piece, coord, (rank,column), capture=True))
                break
            else:
                break
            rank += vector[0]
            column += vector[1]
    else:
        raise Exception("Invalid Active Color")
    return actions

def add_vectors(coord, vector):
    """Add a vector to a coordinate and return the new coordinate."""
    return tuple(c1+c2 for c1,c2 in zip(coord, vector))

def get_bishop_moves(state, coord):
    """Returns the moves for the bishop at the given location
    """
    # Movement Options
    # Diagonals
    # no piece = add move, enemy = add move & break loop, friendly = break loop

    bishop_moves = []        

    if state.active_color == cc.WHITE_ACTIVE:
        for vector in cc.BISHOP_VECTORS:
            bishop_moves.extend(get_direction_moves(state, cc.W_BISHOP, coord, vector))
            
    elif state.active_color == cc.BLACK_ACTIVE:
        for vector in cc.BISHOP_VECTORS:
            bishop_moves.extend(get_direction_moves(state, cc.B_BISHOP, coord, vector))
    else:
        raise Exception("GameState: Invalid Active Color")
    return bishop_moves

def get_rook_moves(state, coord):
    """Returns the moves for the rook at the given location
    """
    rook_moves = []

    if state.active_color == cc.WHITE_ACTIVE:
        for vector in cc.ROOK_VECTORS:
            rook_moves.extend(get_direction_moves(state, cc.W_ROOK, coord, vector))

    elif state.active_color == cc.BLACK_ACTIVE:
        for vector in cc.ROOK_VECTORS:
            rook_moves.extend(get_direction_moves(state, cc.B_ROOK, coord, vector))
    else:
        raise Exception("GameState: Invalid Active Color")
    return rook_moves

def get_queen_moves(state, coord):
    """Returns the moves for the queen at the given location
    """
    queen_moves = []
    if state.active_color == cc.WHITE_ACTIVE:
        for vector in cc.QUEEN_VECTORS:
            queen_moves.extend(get_direction_moves(state, cc.W_QUEEN, coord, vector))
    elif state.active_color == cc.BLACK_ACTIVE:
        for vector in cc.QUEEN_VECTORS:
            queen_moves.extend(get_direction_moves(state, cc.B_QUEEN, coord, vector))
    else:
        raise Exception("GameState: Invalid Active Color")
    return queen_moves


def validate_moves(moves):
    """Check if all the moves are on the board.
    Returns a tuple of booleans that map to the moves. True if valid, False if invalid
    """
    valid_coords = []
    for move in moves:
        if move[0] in cc.VALID_RANKS and move[1] in cc.VALID_RANKS:
            valid_coords.append(True)
        else:
            valid_coords.append(False)
    return tuple(valid_coords)

def validate_move(move):
    """Check if a single move is on the board.
    Returns boolean.
    """
    if move[0] in cc.VALID_RANKS and move[1] in cc.VALID_RANKS:
        valid = True
    else:
        valid = False
    return valid