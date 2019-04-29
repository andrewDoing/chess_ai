from games.chess import chess_classes as cc
from games.chess import get_moves as gm

def check_direction(state, coord, vector, attack_color):
    """Loops through the board in the direction specified. 
    Returns the first piece encountered and its location.
    """
    if attack_color == cc.WHITE_ACTIVE:
        # Determine the possible attackers
        if vector in cc.BISHOP_VECTOR_SET:
            enemy_pieces = {cc.W_BISHOP, cc.W_QUEEN}
        elif vector in cc.ROOK_VECTOR_SET:
            enemy_pieces = {cc.W_ROOK, cc.W_QUEEN}
        # Loop
        rank = coord[0] + vector[0]
        column = coord[1] + vector[1]
        while rank in cc.VALID_RANKS and column in cc.VALID_RANKS:
            if state.board[rank, column] in enemy_pieces:
                return True, (state.board[rank, column], (rank, column))
            elif state.board[rank, column] in cc.BLACK_PIECES:
                return False, None
            rank += vector[0]
            column += vector[1]
        # Finished looping, no attacker
        return False, None
    elif attack_color ==cc.BLACK_ACTIVE:
        # Determine the possible attackers
        if vector in cc.BISHOP_VECTOR_SET:
            enemy_pieces = {cc.B_BISHOP, cc.B_QUEEN}
        elif vector in cc.ROOK_VECTOR_SET:
            enemy_pieces = {cc.B_ROOK, cc.B_QUEEN}
        # Loop
        rank = coord[0] + vector[0]
        column = coord[1] + vector[1]
        while rank in cc.VALID_RANKS and column in cc.VALID_RANKS:
            if state.board[rank, column] in enemy_pieces:
                return True, (state.board[rank, column], (rank, column))
            elif state.board[rank, column] in cc.WHITE_PIECES:
                return False, None
            rank += vector[0]
            column += vector[1]
        # Finished looping, no attacker
        return False, None
    else:
        raise Exception("Wrong color")

def space_under_attack(state, coord, attack_color):
    """Given a space, return whether it is under attack or not"""
    # Find the possible moves
    valid_knights = gm.get_crawler_moves(coord, cc.KNIGHT_VECTORS)
    valid_kings = gm.get_crawler_moves(coord, cc.KING_VECTORS)

    if attack_color == cc.WHITE_ACTIVE:
        # Pawns are moving up the board
        p_attack_1 = (coord[0]+1, coord[1]-1)
        p_attack_2 = (coord[0]+1, coord[1]+1)
        # Check if the movement coordinates are on the board
        p_attack_1_valid = gm.validate_move(p_attack_1)
        p_attack_2_valid = gm.validate_move(p_attack_2)

        # Check for Pawns
        if p_attack_1_valid and state.board[p_attack_1] == cc.W_PAWN:
            return True
        if p_attack_2_valid and state.board[p_attack_2] == cc.W_PAWN:
            return True
        # Knights
        for knight in valid_knights:
            if state.board[knight] == cc.W_KNIGHT:
                return True
        # Kings
        for king in valid_kings:
            if state.board[king] == cc.W_KING:
                return True
        # Bishops and Queens
        for vector in cc.BISHOP_VECTORS:
            valid, attacker = check_direction(state, coord, vector, attack_color)
            if valid:
                return True
        # Rooks and Queens
        for vector in cc.ROOK_VECTORS:
            valid, attacker = check_direction(state, coord, vector, attack_color)
            if valid:
                return True
        return False

    elif attack_color == cc.BLACK_ACTIVE:
        # Pawns are moving down the board
        p_attack_1 = (coord[0]-1, coord[1]-1)
        p_attack_2 = (coord[0]-1, coord[1]+1)
        # Check if the movement coordinates are on the board
        p_attack_1_valid = gm.validate_move(p_attack_1)
        p_attack_2_valid = gm.validate_move(p_attack_2)
        # Check for Pawns
        if p_attack_1_valid and state.board[p_attack_1] == cc.B_PAWN:
            return True
        if p_attack_2_valid and state.board[p_attack_2] == cc.B_PAWN:
            return True
        # Knights
        for knight in valid_knights:
            if state.board[knight] == cc.B_KNIGHT:
                return True
        # Kings
        for king in valid_kings:
            if state.board[king] == cc.B_KING:
                return True
        # Bishops and Queens
        for vector in cc.BISHOP_VECTORS:
            valid, attacker = check_direction(state, coord, vector, attack_color)
            if valid:
                return True, attacker
        # Rooks and Queens
        for vector in cc.ROOK_VECTORS:
            valid, attacker = check_direction(state, coord, vector, attack_color)
            if valid:
                return True, attacker
        return False
    else:
        raise Exception('space_under_attack: Invalid Enemy Color')

def get_attackers(state, coord, attack_color):
    """Given a space, return the attackers of the space
    """
    # Find the possible moves
    possible_knights = gm.get_crawler_moves(coord, cc.KNIGHT_VECTORS)
    possible_kings = gm.get_crawler_moves(coord, cc.KING_VECTORS)

    attackers = []

    if attack_color == cc.WHITE_ACTIVE:
        # Pawns are moving up the board
        p_attack_1 = (coord[0]+1, coord[1]-1)
        p_attack_2 = (coord[0]+1, coord[1]+1)
        # Check if the movement coordinates are on the board
        p_attack_1_valid = gm.validate_move(p_attack_1)
        p_attack_2_valid = gm.validate_move(p_attack_2)

        # Check for Pawns
        if p_attack_1_valid and state.board[p_attack_1] == cc.W_PAWN:
            attackers.append((cc.W_PAWN, p_attack_1))
        if p_attack_2_valid and state.board[p_attack_2] == cc.W_PAWN:
            attackers.append((cc.W_PAWN, p_attack_2))
        # Knights
        for knight in possible_knights:
            if state.board[knight] == cc.W_KNIGHT:
                attackers.append((cc.W_KNIGHT, knight))
        # Kings
        for king in possible_kings:
            if state.board[king] == cc.W_KING:
                attackers.append((cc.W_KING, king))
        # Bishops and Queens
        for vector in cc.BISHOP_VECTORS:
            valid, attacker = check_direction(state, coord, vector, attack_color)
            if valid:
                attackers.append(attacker)
        # Rooks and Queens
        for vector in cc.ROOK_VECTORS:
            valid, attacker = check_direction(state, coord, vector, attack_color)
            if valid:
                attackers.append(attacker)

    elif attack_color == cc.BLACK_ACTIVE:
        # Pawns are moving down the board
        p_attack_1 = (coord[0]-1, coord[1]-1)
        p_attack_2 = (coord[0]-1, coord[1]+1)
        # Check if the movement coordinates are on the board
        p_attack_1_valid = gm.validate_move(p_attack_1)
        p_attack_2_valid = gm.validate_move(p_attack_2)
        # Check for Pawns
        if p_attack_1_valid and state.board[p_attack_1] == cc.B_PAWN:
            attackers.append((cc.B_PAWN, p_attack_1))
        if p_attack_2_valid and state.board[p_attack_2] == cc.B_PAWN:
            attackers.append((cc.B_PAWN, p_attack_2))
        # Knights
        for knight in possible_knights:
            if state.board[knight] == cc.B_KNIGHT:
                attackers.append((cc.B_KNIGHT, knight))
        # Kings
        for king in possible_kings:
            if state.board[king] == cc.B_KING:
                attackers.append((cc.B_KING, king))
        # Bishops and Queens
        for vector in cc.BISHOP_VECTORS:
            valid, attacker = check_direction(state, coord, vector, attack_color)
            if valid:
                attackers.append(attacker)
        # Rooks and Queens
        for vector in cc.ROOK_VECTORS:
            valid, attacker = check_direction(state, coord, vector, attack_color)
            if valid:
                attackers.append(attacker)

    else:
        raise Exception('space_under_attack: Invalid Enemy Color')

    return tuple(attackers)

