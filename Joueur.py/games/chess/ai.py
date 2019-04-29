# This is where you build your AI for the Chess game.
import numpy as np
import random
import sys

from joueur.base_ai import BaseAI

from games.chess import chess_classes as cc
from games.chess import get_moves as gm
from games.chess import check
from games.chess import interface
from games.chess import search


def pretty_fen(fen, us):
    """
    Pretty formats an FEN string to a human readable string.

    For more information on FEN (Forsyth-Edwards Notation) strings see:
    https://wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
    """

    # split the FEN string up to help parse it
    split = fen.split(' ')
    first = split[0]  # the first part is always the board locations

    side_to_move = split[1]  # always the second part for side to move
    us_or_them = 'us' if side_to_move == us[0] else 'them'

    fullmove = split[5]  # always the sixth part for the full move

    lines = first.split('/')
    strings = ['Move: {}\nSide to move: {} ({})\n   +-----------------+'.format(
        fullmove, side_to_move, us_or_them
    )]

    for i, line in enumerate(lines):
        strings.append('\n {} |'.format(8 - i))
        for char in line:
            try:
                char_as_number = int(char)
                # it is a number, so that many blank lines
                strings.append(' .' * char_as_number)
            except:
                strings.append(' ' + char)

        strings.append(' |')
    strings.append('\n   +-----------------+\n     a b c d e f g h\n')

    return ''.join(strings)

class AI(BaseAI):
    """ The AI you add and improve code inside to play Chess. """

    @property
    def game(self):
        """The reference to the Game instance this AI is playing.

        :rtype: games.chess.game.Game
        """
        return self._game  # don't directly touch this "private" variable pls

    @property
    def player(self):
        """The reference to the Player this AI controls in the Game.

        :rtype: games.chess.player.Player
        """
        return self._player  # don't directly touch this "private" variable pls

    def get_name(self):
        """ This is the name you send to the server so your AI will control the
            player named this string.

        Returns
            str: The name of your Player.
        """
        return "DryPyChess"  # REPLACE THIS WITH YOUR TEAM NAME

    def start(self):
        """ This is called once the game starts and your AI knows its player and
            game. You can initialize your AI here.
        """
        self.state = interface.fen_to_GameState(self.game.fen)
        self.history_table = {}

    def game_updated(self):
        """ This is called every time the game's state updates, so if you are
        tracking anything you can update it here.
        """
        self.state = interface.fen_to_GameState(self.game.fen)
        self.state.history = self.game.history

    def end(self, won, reason):
        """ This is called when the game ends, you can clean up your data and
            dump files here if need be.

        Args:
            won (bool): True means you won, False means you lost.
            reason (str): The human readable string explaining why your AI won
            or lost.
        """
        #print(self.game.history)
        # replace with your end logic

    def make_move(self):
        """ This is called every time it is this AI.player's turn to make a move.

        Returns:
            str: A string in Standard Algebraic Notation (SAN) for the move you want to make. If the move is invalid or not properly formatted you will lose the game.


        *******************************************************************************************************
        * IMPORTANT SERVER VARIABLES TO KNOW:
        *******************************************************************************************************
        * 
        * * Game.History
        *      - The list of moves that have occurred in the game so far in SAN.
        *
        * * Game.Fen
        *      - The FEN string representing the current board state. Updated every turn
        *      - For more info about FEN strings: https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
        *
        * * Player
        *      - Your player object.
        *      - Important properties:
        *          * Player.Color
        *              - Your client's color ("white" or "black")
        *          * Player.Opponent
        *              - Your opponent's player object.
        *
        * NOTE THAT ALL OBJECT INFORMATION IS CONTAINED IN Joueur.py/games/chess/
        * HOWEVER, DO NOT CHANGE ANY OF THESE FILES EXCEPT FOR ai.py AND ANY OTHER FILES YOU MAY ADD YOURSELF
        * 
        *******************************************************************************************************
        * STANDARD ALGEBRAIC NOTATION
        *******************************************************************************************************
        * 
        * * When returning your move in Standard Algebraic Notation (SAN), the way I recommend is to first
        *   indicate the piece type if the piece is not a pawn, then the starting square's file and rank, then
        *   an x if there is a capture, then the ending square's file and rank.
        *   
        * * Pieces are indicated as R for Rook, N for Knight, B for Bishop, Q for Queen, and K for King. Pawns
        *   are not denoted by any letter.
        * 
        * * For castling in SAN, king-side castling is indicated by "O-O", while queen-side castling is
        *   indicated by "O-O-O".
        *
        * * To promote a pawn when it reaches the other side of the board, add the type of piece to promote to
        *   at the end of the string.
        *   
        * * All SAN is case sensitive.
        * 
        * * Some examples:
        *      - Move a pawn from a2 to a4: a2a4
        *      - Capture a piece with a pawn from c6 to d5: c6xd5
        *      - Move a knight from b1 to c3: Nb1c3
        *      - Capture a piece with a queen from h3 to e6: Qh3xe6
        *      - King-side castle: O-O
        *      
        * * For more info about SAN: https://en.wikipedia.org/wiki/Algebraic_notation_(chess)
        * 
        *******************************************************************************************************

        """
        time_percentage = self.get_setting("time_percentage")
        if time_percentage == None:
            # Default Value
            time_percentage = 0.01 #1%
        else:
            try:
                time_percentage = float(time_percentage)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise

        qs_depth = self.get_setting("qs_depth")
        if qs_depth == None:
            # Default Value
            qs_depth = 2
        else:
            try:
                qs_depth = int(qs_depth)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise

        root = search.SearchNode(self.state, None)

        best_action_values = search.tl_ht_qs_ab_id_dl_minimax(root, qs_depth, self.history_table, time_percentage, self.player.time_remaining)
        print("Best Action + Values: {}".format(best_action_values))

        while best_action_values:
            bav = best_action_values.pop()
            if bav[0] is not None:
                chosen_action = bav[0]
                break

        san_string = interface.san(chosen_action)
        print("SAN: {}".format(san_string))
        
        return san_string