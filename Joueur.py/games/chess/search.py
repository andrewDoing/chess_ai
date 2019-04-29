import pickle
import random
import time
from contextlib import contextmanager

from anytree import NodeMixin

from queue import Queue, PriorityQueue
from math import inf as infinity
from itertools import count

from games.chess import chess_classes as cc
from games.chess import get_moves as gm
from games.chess import check
from games.chess import interface

# Data Structure for the information in each node
class NodeData:
    # Constructor
    def __init__(self, state, action, path_cost=0, heuristic=None):
        self.state = state
        self.action = action
        self.heuristic = heuristic

    # String Output Definition
    def __str__(self):
        return self.state.__str__() + "\n" + "Action: " + self.action + "\n" + "h(n): " + self.heuristic

# Tree Node definition. Uses NodeMixin to add TreeNode properties
class SearchNode(NodeData, NodeMixin):
    __slots__ = ['state', 'action', 'path_cost', 'heuristic', 'parent', 'children']
    def __init__(self, state, action, path_cost=0, heuristic=None, parent=None):
        super().__init__(state, action, path_cost, heuristic)
        self.parent = parent

    # String Output Definition
    def __str__(self):
        return super().__str__() + "\n" + "Parent: " + self.parent

    def __lt__(self, other):
        return self.heuristic < other.heuristic

def is_nonquiescent(actions):
    """Returns a boolean as to whether the current state is a terminal.
    Based on whether the actions available in the state are:
        -Capture opponent’s piece
        -Opponent put into Check TODO
        -Promotion of a Pawn
    """
    for action in actions:
        if action.capture == True:
            return True
        if action.promo is not None:
            return True
    else:
        return False

def is_terminal(node):
    """Returns a boolean as to whether the node is a terminal. AKA Draw or Checkmate
    """
    if is_checkmate(node.state):
        return True
    elif is_draw(node.state, node.state.history):
        return True
    else:
        return False

def is_draw(state, history):
    # Insufficient Material
    white_material = state.get_pieces(cc.WHITE_ACTIVE)
    black_material = state.get_pieces(cc.BLACK_ACTIVE)
    
    # Black and White each only have their kings
    if len(white_material) == 1 and len(black_material) == 1:
        return True
    # White only has King
    if len(white_material) == 1:
        if len(black_material) == 2 and cc.B_BISHOP in black_material:
            if black_material[cc.B_BISHOP] == 1:
                return True
        elif len(black_material) == 2 and cc.B_KNIGHT in black_material:
            if black_material[cc.B_KNIGHT] == 1:
                return True
        else:
            return False
    # Black only has King
    elif len(black_material) == 1:
        if len(white_material) == 2 and cc.W_BISHOP in white_material:
            if white_material[cc.W_BISHOP] == 1:
                return True
        elif len(white_material) == 2 and cc.W_KNIGHT in white_material:
            if white_material[cc.W_KNIGHT] == 1:
                return True
        else:
            return False

    # Stalemate. King not in check, no valid moves
    king = state.find_king(state.active_color)
    if not check.space_under_attack(state, king, state.opp_color):
        # Check if there are any valid moves
        p_actions = actions(state)
        v_actions = validate_actions(state, p_actions)
        if not v_actions:
            return True
    
    # Three State Repetition Rule
    if len(history) >= 8:
        sev_action = history[-1] # Last move
        six_action = history[-2] # 2nd to last
        five_action = history[-3]
        four_action = history[-4]
        three_action = history[-5]
        two_action   = history[-6]
        one_action   = history[-7]
        zero_action  = history[-8]
        if zero_action == four_action and \
            one_action == five_action and \
            two_action == six_action and \
            three_action == sev_action:
            return True

    # 50 move rule. 100, because 2 actions = 1 move
    if len(history) >= 100:
        for idx in range(-1, -101, -1):
            # Pawn Move
            if history[idx][0] not in cc.WHITE_PIECES:
                return False
            if "x" in history[idx]:
                return False
        return True

def is_checkmate(state):
    """Returns a boolean as to whether the active color's king is in checkmate.
    """
    in_check = check.space_under_attack(state, state.active_king, state.opp_color)
    if in_check:
        # Are there any valid moves?
        p_actions = actions(state)
        v_actions = validate_actions(state, p_actions)
        if not v_actions:
            return True
        else:
            return False
    else:
        # King is not in check, therefore he can't be in checkmate
        return False

def validate_actions(state, possible_action_list):
    valid_action_list = []
    # Validate actions
    for action in possible_action_list:
        new_state = result(state, action)
        if check.space_under_attack(new_state, new_state.inactive_king, new_state.active_color):
            continue
        else:
            valid_action_list.append(action)

    return valid_action_list

def actions(state):
    """Take GameState and find all the valid actions the player can take.
    Structure of an Action Tuple:
        - Piece: Piece Constant
        - Previous Location (RANK, FILE)
        - New Location (RANK, FILE)
        - Capture? 1 otherwise 0
        - Castling? 1 character following FEN, otherwise -
        - Promotion? Indicates which piece the pawn becomes, otherwise -
    """
    action_list = []

    if state.active_color == cc.WHITE_ACTIVE:
        active_pieces = cc.WHITE_PIECES
    elif state.active_color == cc.BLACK_ACTIVE:
        active_pieces = cc.BLACK_PIECES
    else:
        raise Exception("Actions: Invalid Active Color")
    # Check for states where castling can occur
    castles = gm.get_castle(state)
    if castles[0]: # Kingside Castle
        action_list.append(cc.Action(piece=cc.W_KING, castle=cc.CASTLE_KINGSIDE))
    if castles[1]: # Queenside Castle
        action_list.append(cc.Action(piece=cc.W_KING, castle=cc.CASTLE_QUEENSIDE))

    # Loop over the board, finding the moves for each piece
    for rank in range(8):
        for column in range(8):
            if state.board[rank, column] in active_pieces:
                p = gm.Piece(state.board[rank, column], (rank, column))
                action_list.extend(p.get_moves(state))

    # Handle En passant attacks
    for action in action_list:
        if action.end == state.en_passant:
            action.capture = True

    return action_list

def result(state, action):
    """Returns the new GameState from the passed state after applying the action"""
    # Faster than deepcopy
    new_state = pickle.loads(pickle.dumps((state)))

    if action.castle == None:
        # Attacking En passant pawn
        if new_state.en_passant == action.end:
            new_state.board[action.start] = cc.NO_PIECE
            new_state.board[action.end] = action.piece
            # Delete black pawn
            if new_state.en_passant[0] == cc.RANK_6:
                down = (action.end[0]+1, action.end[1])
                new_state.board[down] = cc.NO_PIECE
            # Delete white pawn
            elif new_state.en_passant[0] == cc.RANK_3:
                up = (action.end[0]-1, action.end[1])
                new_state.board[up] = cc.NO_PIECE
        # Default Case
        else:
            # Delete piece from the start
            new_state.board[action.start] = " "
            # Place piece at the end
            new_state.board[action.end] = action.piece

        # Set en_passant space for a pawn moving 2
        if action.en_p:
            new_state.en_passant = cc.coord_to_alg(action.en_p)
        else:
            new_state.en_passant = cc.NO_C_EP

        # Remove castle availability if the rook or king move
        if action.piece == cc.W_ROOK:
            if action.start == (cc.RANK_1, cc.FILE_H):
                new_state.castles_avail = new_state.castles_avail.replace('K', '')
            elif action.start == (cc.RANK_1, cc.FILE_A):
                new_state.castles_avail = new_state.castles_avail.replace('Q', '')
        elif action.piece == cc.W_KING:
            if action.start == (cc.RANK_1, cc.FILE_E):
                new_state.castles_avail = new_state.castles_avail.replace('K', '')
                new_state.castles_avail = new_state.castles_avail.replace('Q', '')
        elif action.piece == cc.B_ROOK:
            if action.start == (cc.RANK_8, cc.FILE_H):
                new_state.castles_avail = new_state.castles_avail.replace('k', '')
            elif action.start == (cc.RANK_8, cc.FILE_A):
                new_state.castles_avail = new_state.castles_avail.replace('q', '')
        elif action.piece == cc.B_KING:
            if action.start == (cc.RANK_8, cc.FILE_E):
                new_state.castles_avail = new_state.castles_avail.replace('k', '')
                new_state.castles_avail = new_state.castles_avail.replace('q', '')

        # Update the halfmove count
        if action.capture or action.piece == cc.W_PAWN or action.piece == cc.B_PAWN:
            new_state.halfmove = 0
        else:
            new_state.halfmove += 1
        
    else: # Castle Time
        if action.castle == cc.CASTLE_QUEENSIDE:
            if state.active_color == cc.WHITE_ACTIVE:
                # Delete and Place Rook
                new_state.board[cc.RANK_1, cc.FILE_A] = " "
                new_state.board[cc.RANK_1, cc.FILE_D] = cc.W_ROOK
                # Delete and Place King
                new_state.board[cc.RANK_1, cc.FILE_E] = " "
                new_state.board[cc.RANK_1, cc.FILE_C] = cc.W_KING
                # Remove all White castling availability
                new_state.castles_avail = new_state.castles_avail.replace('K','')
                new_state.castles_avail = new_state.castles_avail.replace('Q','')
                # If the string is empty, replace with a dash
                if not new_state.castles_avail:
                    new_state.castles_avail = cc.NO_C_EP
            elif state.active_color == cc.BLACK_ACTIVE:
                # Delete and Place Rook
                new_state.board[cc.RANK_8, cc.FILE_A] = " "
                new_state.board[cc.RANK_8, cc.FILE_D] = cc.B_ROOK
                # Delete and Place King
                new_state.board[cc.RANK_8, cc.FILE_E] = " "
                new_state.board[cc.RANK_8, cc.FILE_C] = cc.B_KING
                # Remove all Black castling availability
                new_state.castles_avail = new_state.castles_avail.replace('k','')
                new_state.castles_avail = new_state.castles_avail.replace('q','')
                # If the string is empty, replace with a dash
                if not new_state.castles_avail:
                    new_state.castles_avail = cc.NO_C_EP

        elif action.castle == cc.CASTLE_KINGSIDE:
            if state.active_color == cc.WHITE_ACTIVE:
                # Delete and Place Rook
                new_state.board[cc.RANK_1, cc.FILE_H] = " "
                new_state.board[cc.RANK_1, cc.FILE_F] = cc.W_ROOK
                # Delete and Place King
                new_state.board[cc.RANK_1, cc.FILE_E] = " "
                new_state.board[cc.RANK_1, cc.FILE_G] = cc.W_KING
                # Remove all White castling availability
                new_state.castles_avail = new_state.castles_avail.replace('K','')
                new_state.castles_avail = new_state.castles_avail.replace('Q','')
                # If the string is empty, replace with a dash
                if not new_state.castles_avail:
                    new_state.castles_avail = cc.NO_C_EP
            elif state.active_color == cc.BLACK_ACTIVE:
                # Delete and Place Rook
                new_state.board[cc.RANK_8, cc.FILE_H] = " "
                new_state.board[cc.RANK_8, cc.FILE_F] = cc.B_ROOK
                # Delete and Place King
                new_state.board[cc.RANK_8, cc.FILE_E] = " "
                new_state.board[cc.RANK_8, cc.FILE_G] = cc.B_KING
                # Remove all Black castling availability
                new_state.castles_avail = new_state.castles_avail.replace('k','')
                new_state.castles_avail = new_state.castles_avail.replace('q','')
                # If the string is empty, replace with a dash
                if not new_state.castles_avail:
                    new_state.castles_avail = cc.NO_C_EP
    
    # Update fullmove count
    if new_state.active_color == cc.WHITE_ACTIVE:
        new_state.active_color = cc.BLACK_ACTIVE
        new_state.opp_color = cc.WHITE_ACTIVE
    else:
        new_state.active_color = cc.WHITE_ACTIVE
        new_state.opp_color = cc.BLACK_ACTIVE
        new_state.fullmove += 1

    new_state.active_king = new_state.find_king(new_state.active_color)
    new_state.inactive_king = new_state.find_king(new_state.opp_color)

    return new_state

def update_history_table(history_table, state, move):
    string = get_history_string(state, move)
    if string in history_table:
        value = history_table[string]
        value += 1
        history_table[string] = value
    else:
        history_table[string] = 1

def get_history_string(state, move):
    state_string = state.get_fen()
    move_string = interface.san(move)
    return state_string+" "+move_string

def history_table_sort(history_table, state, moves):
    q = PriorityQueue()
    unique = count()
    sorted_moves = []

    for move in moves:
        # Concat the state and move strings
        string = get_history_string(state, move)
        if string in history_table:
            priority = history_table[string]
        else:
            priority = 0
        q.put((priority, next(unique), move))

    #Change priority queue back to a list of moves
    for entry in q.queue:
        sorted_moves.append(entry[2])
    return sorted_moves

def tl_ht_qs_ab_id_dl_minimax(node, qs_depth, history_table, percentage, time_remaining):
    """Time Limited, Alpha Beta Pruning, Iterative Deepening,
    Depth Limited MiniMax.
    TODO:
    - Use a generator with a time limit
    """
    values = []

    # Handle a time limit
    start_time = time.time()
    seconds = int(time_remaining * percentage / 1000000000)
    end_time = start_time + seconds
    # Start Depth at 1, increase until time limit is reached
    depth = 1
    
    while time.time() < end_time:
        values.append(ht_qs_ab_dl_minimax(node, depth, qs_depth, end_time, history_table))
        depth += 1
    return values

def maxv(node, depth, qs_depth, alpha, beta, player, end_time, history_table):
    """Max Player Logic"""
    if (depth == 0 and qs_depth == 0) or is_terminal(node):
        return heuristic(node.state, player)
    
    possible_actions = actions(node.state)
    valid_actions = validate_actions(node.state, possible_actions)
    nonquiescent = is_nonquiescent(valid_actions)
    
    if depth == 0 and not nonquiescent:
        return heuristic(node.state, player)

    # Randomize Moves
    random.shuffle(valid_actions)
    # History Table Sort
    valid_actions = history_table_sort(history_table, node.state, valid_actions)

    best_value = -infinity
    if valid_actions:
        best_move = valid_actions[0]

    frontier = Queue()

    for action in valid_actions:
        frontier.put(
            SearchNode(
                result(node.state, action),
                action
            )
        )

    while not frontier.empty():
        new_node = frontier.get()
        # Recursive call
        if depth == 0 and nonquiescent:
            value = minv(new_node, depth, qs_depth-1, alpha, beta, player, end_time, history_table)
        else:
            value = minv(new_node, depth-1, qs_depth, alpha, beta, player, end_time, history_table)
        # Check if the time has expired
        if time.time() > end_time:
            break
        # If the value is better than the previous best, replace it
        if value > best_value:
            best_value = value
            best_move = new_node.action
        # If the new best is better than alpha, set alpha to it
        if best_value > alpha:
            alpha = best_value
        # Fail High
        if alpha >= beta:
            break

    update_history_table(history_table, node.state, best_move)
    return best_value

def minv(node, depth, qs_depth, alpha, beta, player, end_time, history_table):
    """Min Player Logic"""
    if depth == 0 or is_terminal(node):
        return heuristic(node.state, player)
    
    possible_actions = actions(node.state)
    valid_actions = validate_actions(node.state, possible_actions)
    nonquiescent = is_nonquiescent(valid_actions)
    
    if depth == 0 and not nonquiescent:
        return heuristic(node.state, player)

    # Randomize Moves
    random.shuffle(valid_actions)
    # History Table Sort
    valid_actions = history_table_sort(history_table, node.state, valid_actions)

    best_value = +infinity
    if valid_actions:
        best_move = valid_actions[0]

    frontier = Queue()

    for action in valid_actions:
        frontier.put(
            SearchNode(
                result(node.state, action),
                action
            )
        )

    while not frontier.empty():
        new_node = frontier.get()
        # Recursive call
        if depth == 0 and nonquiescent:
            value = maxv(new_node, depth, qs_depth-1, alpha, beta, player, end_time, history_table)
        else:
            value = maxv(new_node, depth-1, qs_depth, alpha, beta, player, end_time, history_table)
        # Check if the time has expired
        if time.time() > end_time:
            break
        # If the value is better than the previous best, replace it
        if value < best_value:
            best_value = value
            best_move = new_node.action
        # If the new best is lower than beta, set beta to it
        if best_value < beta:
            beta = best_value
        # Fail Low
        if beta <= alpha:
            break
    
    update_history_table(history_table, node.state, best_move)
    return best_value


def ht_qs_ab_dl_minimax(node, depth, qs_depth, end_time, history_table):
    """AI function that finds the best move to make.
    :return: Action object
    """

    alpha, beta = -infinity, infinity
    player = node.state.active_color

    possible_actions = actions(node.state)
    valid_actions = validate_actions(node.state, possible_actions)
    
    # Randomize Moves
    random.shuffle(valid_actions)
    # History Table Sort
    valid_actions = history_table_sort(history_table, node.state, valid_actions)

    best_value = -infinity
    if valid_actions:
        best_move = valid_actions[0]
    
    frontier = Queue()

    for action in valid_actions:
        frontier.put(
            SearchNode(
                result(node.state, action),
                action
            )
        )
    
    while not frontier.empty():
        new_node = frontier.get()
        # Recursive call
        value = minv(new_node, depth-1, qs_depth, alpha, beta, player, end_time, history_table)
        
        # Check if the time has expired
        if time.time() > end_time:
            break
        # If the value is better than the previous best, replace it
        if value > best_value:
            best_value = value
            best_move = new_node.action
        # If the new best is better than alpha, set alpha to it
        if best_value > alpha:
            alpha = best_value
        # Fail High
        if alpha >= beta:
            break
    
    update_history_table(history_table, node.state, best_move)
    return (best_move, best_value)


def heuristic(state, player):
    """Interface Logic for the heuristic
    """
    if is_checkmate(state):
        if state.active_color == cc.WHITE_ACTIVE:
            return -9999
        else:
            return 9999
    else:
        return material_advantage(state, player)

def material_advantage(state, player):
    """Returns a number that reflects the material advantage of the passed color"""
    ma = 0
    if player == cc.WHITE_ACTIVE:
        white_factor = 1
        black_factor = -1
    else:
        white_factor = -1
        black_factor = 1
    
    for rank in range(8):
        for column in range(8):
            piece = state.board[rank, column]
            if piece == cc.NO_PIECE:
                continue
            elif piece in cc.WHITE_PIECES:
                if piece == cc.W_PAWN:
                    ma += white_factor * cc.MA_PAWN
                elif piece == cc.W_KNIGHT:
                    ma += white_factor * cc.MA_KNIGHT
                elif piece == cc.W_BISHOP:
                    ma += white_factor * cc.MA_BISHOP
                elif piece == cc.W_ROOK:
                    ma += white_factor * cc.MA_ROOK
                elif piece == cc.W_QUEEN:
                    ma += white_factor * cc.MA_QUEEN
                elif piece == cc.W_KING:
                    ma += white_factor * cc.MA_KING
            elif piece in cc.BLACK_PIECES:
                if piece == cc.B_PAWN:
                    ma += black_factor * cc.MA_PAWN
                elif piece == cc.B_KNIGHT:
                    ma += black_factor * cc.MA_KNIGHT
                elif piece == cc.B_BISHOP:
                    ma += black_factor * cc.MA_BISHOP
                elif piece == cc.B_ROOK:
                    ma += black_factor * cc.MA_ROOK
                elif piece == cc.B_QUEEN:
                    ma += black_factor * cc.MA_QUEEN
                elif piece == cc.B_KING:
                    ma += black_factor * cc.MA_KING
    return ma