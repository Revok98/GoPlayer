"""
version avec les réseaux de neurones
"""
import numpy as np
from random import choice
import sys
from tensorflow import keras
from import_data import board_encoding


class MCTS:
    def __init__(self, game, father=None, move=None, prior=0):
        self.father = father
        self.children = list()
        self.move = move
        self.N = 0
        self.W = 0
        self.Q = 0
        self.P = prior

    def is_leaf(self):
        return len(self.children) == 0

    def is_root(self):
        return self.father == None

    def U(self):
        return P * np.sqrt(self.father.N / self.N)

    def selection(self, game):
        if not self.is_root():
            game.push(self.move)
        if self.is_leaf():
            return self
        if not self.game_over:
            c = np.argmax([n.Q + n.U() for n in self.children])
            return self.children[c].selection(game)
        return self

    def expansion(self, game, nn_priors, nn_values):
        P = nn_priors.predict(np.array([board_encoding(game)]))[0] # TODO: non testé!!
        V = nn_values.predict(np.array([board_encoding(game)]))[0] # TODO: non testé!!
        for move in game.legal_moves():
            game.push(move)
            node = MCTS(game, self, move, P[i])
            game.pop()
            self.children.append(node)
        return V

    def back(self, V):
        self.N = N + 1
        self.W = W + V
        self.Q = self.W / self.N
        if self.father != None:
            self.father.back(V)

    def select_move_deterministically(self):
        best = self.children[0]
        for i in range(1, len(self.children)):
            if self.children[i].N > best.N:
                best = self.children[i]
        return best.move

    def select_move_stochastically(self):
        s = sum([c.N for c in self.children])
        r = np.random.randint(s)
        s = 0
        for child in self.children:
            s += child.N
            if s > r:
                return child.move

class MCTS_TREE:
    def __init__(self, game):
        self.root = MCTS(game)
        self.nn_priors = keras.models.load_model('model/model_priors.h5')
        self.nn_values = keras.models.load_model('model/model_values.h5')

    def apply_mcts(self, game, iterations, color):
        for _ in range(iterations):
            #game = original_game.copy()
            n = self.root.selection(game)
            v = n.expansion(game, self.nn_priors, self.nn_values)
            n.backpropagate(game, v)
        return self.root.select_move_deterministically()

    def relocate_root(self, game, move):
        for c in self.root.children:
            if c.move == move:
                self.root = c
                self.root.father = None
                self.root.move = None
        self.root = MCTS(game)
