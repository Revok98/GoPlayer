# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

import time
import Goban
from random import choice
import random
from playerInterface import *
import numpy as np

from mctsNN import MCTS_TREE

class myPlayer(PlayerInterface):
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!
    '''

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self.tree = MCTS_TREE(self._board)

    def getPlayerName(self):
        return "MCTS Player"

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"

        start_time = time.time()
        move = self.tree.apply_mcts(self._board, 50, self._mycolor)
        #print(f"time {time.time() - start_time}")
        self.tree.relocate_root(self._board, move)

        self._board.push(move)
        # New here: allows to consider internal representations of moves
        #print("I am playing ", self._board.move_to_str(move))
        #print("My current board :")
        #self._board.prettyPrint()
        # move is an internal representation. To communicate with the interface I need to change if to a string
        return Goban.Board.flat_to_name(move)

    def playOpponentMove(self, move):
        #print("Opponent played ", move) # New here
        # the board needs an internal represetation to push the move.  Not a string
        move = Goban.Board.name_to_flat(move)
        self._board.push(move)
        self.tree.relocate_root(self._board, move)

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")
