"""
version avec les réseaux de neurones
"""
import numpy as np
from random import choice
import sys
from tensorflow import keras
from import_data import board_encoding


class MCTS_Node:
    def __init__(self, father=None, move=None, prior=0):
        self.father = father
        self.children = list()
        self.move = move
        self.N = 1
        self.W = 0
        self.Q = 0
        self.P = prior

    def is_leaf(self):
        return len(self.children) == 0

    def is_root(self):
        return self.father == None

    def U(self):
        return self.P * np.sqrt(self.father.N / self.N)

    def selection(self, game):
        if not self.is_root():
            game.push(self.move)
        if self.is_leaf():
            return self
        if not game.is_game_over():
            c = np.argmax([n.Q + n.U() for n in self.children])
            return self.children[c].selection(game)
        return self

    def expansion(self, game, nn_priors, nn_values, mycolor):
        if game.is_game_over():
            B, W = game.compute_score()
            if B == W:
                return 0
            if B > W:
                if mycolor == game._BLACK:
                    return 1
                return -1
            if mycolor == game._WHITE:
                return 1
            return -1
        x = board_encoding(game, liberties=3)
        P = nn_priors.predict(np.array([x]))[0]
        V = nn_values.predict(np.array([x]))[0,0]
        for move in game.legal_moves():
            game.push(move)
            node = MCTS_Node(self, move, P[move])
            game.pop()
            self.children.append(node)
        return V

    def back(self, V, game):
        self.N = self.N + 1
        self.W = self.W + V
        self.Q = self.W / self.N
        if not self.is_root():
            game.pop()
            self.father.back(V, game)

    def select_move_deterministically(self):
        best = self.children[0]
        for i in range(1, len(self.children)):
            if self.children[i].N > best.N:
                best = self.children[i]
        return best.move

    def select_move_stochastically(self, game):
        s = sum([c.N for c in self.children])
        r = np.random.randint(s)
        s = 0
        for child in self.children:
            s += child.N
            if s > r:
                return child.move

class MCTS_TREE:
    def __init__(self, game):
        self.root = MCTS_Node()
        self.nn_priors = keras.models.load_model('model/model_priors.h5')
        self.nn_values = keras.models.load_model('model/model_values.h5')

    def apply_mcts(self, game, iterations, color):
        for _ in range(iterations):
            n = self.root.selection(game)
            v = n.expansion(game, self.nn_priors, self.nn_values, color)
            n.back(v, game)
        return self.root.select_move_deterministically()

    def relocate_root(self, move):
        for c in self.root.children:
            if c.move == move:
                self.root = c
                self.root.father = None
                self.root.move = None
                return 
        # si non trouvé, c'est un coup qui n'avait pas encore été exploré
        self.root = MCTS_Node()