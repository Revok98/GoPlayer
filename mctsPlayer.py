# -*- coding: utf-8 -*-

import Goban
from playerInterface import *

from mcts import MCTS_TREE

class myPlayer(PlayerInterface):

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

        move = self.tree.apply_mcts(self._board, 50, self._mycolor)
        self.tree.relocate_root(self._board, move)

        self._board.push(move)
        return Goban.Board.flat_to_name(move)

    def playOpponentMove(self, move):
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
