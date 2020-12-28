"""
version avec les réseaux de neurones
"""
import numpy as np
from random import choice
import sys
from tensorflow import keras
from import_data import board_encoding

class MCTS:
    def __init__(self, game, father=None, move=None, prior=np.inf):
        self.children = list()
        self.game_over = game.is_game_over()
        self.untried_moves = game.legal_moves() if not self.game_over else list()
        self.father = father
        self.n_wins = 0
        self.n_rollout = 0
        self.move = move
        self.prior = prior

    def is_root(self):
        return self.father == None

    def is_leaf(self):
        return self.n_rollout == 0

    def best_child(self):
        max = -1
        best = None
        #l = list()
        for child in self.children:
        #    l.append(child.n_wins / child.n_rollout)
            if child.n_wins / child.n_rollout > max:
                best = child
                max = child.n_wins / child.n_rollout
        #print(f"best move {best.move}: {max} = {best.n_wins} / {best.n_rollout} probability to win")
        #print(l)
        return best

    def value(self):
        if self.n_rollout == 0:
            return self.prior
        return self.n_wins / self.n_rollout + np.sqrt(2 * np.log(self.father.n_rollout/self.n_rollout))

    def selection(self, game):
        if not self.is_root():
            game.push(self.move)
        # s'il reste des coups à explorer
        if len(self.untried_moves) != 0:
            return self
        # sinon, choisir le meilleur selon UCB
        if not self.game_over:
            c = np.argmax([n.value() for n in self.children])
            return self.children[c].selection(game)
        return self

    def expansion(self, game, nn_priors):
        if len(self.untried_moves) != 0:
            priors = nn_priors.predict(np.array([board_encoding(game)]))[0] # TODO: non testé!!
            for move in range(82):
                if move in self.untried_moves:
                    game.push(move)
                    node = MCTS(game, self, move, priors[i])
                    game.pop()
                    self.children.append(node)
                #return node
                # rollout sur le noeud le plus prometteur ?
        return self

    def rollout(self, game, mycolor):
        nbCoupsjoues = 0
        while not game.is_game_over():
            game.push(choice(game.legal_moves()))
            nbCoupsjoues += 1
        (B, W) = game.compute_score()
        for _ in range(nbCoupsjoues):
            game.pop()
        if B == W:
            return 0.5
        if B > W:
            if mycolor == game._BLACK:
                return 1
            return 0
        if mycolor == game._WHITE:
            return 1
        return 0

    def backpropagate(self, game, reward):
        self.n_rollout += 1
        self.n_wins += reward
        if not self.is_root():
            game.pop()
            self.father.backpropagate(game, reward)

class MCTS_TREE:
    def __init__(self, game):
        self.root = MCTS(game)
        self.nn_priors = keras.models.load_model('model/model_priors.h5')
        self.nn_values = keras.models.load_model('model/model_values.h5')

    def apply_mcts(self, game, iterations, color):
        for _ in range(iterations):
            #game = original_game.copy()
            n = self.root.selection(game)
            n = n.expansion(game, self.nn_priors)
            reward = n.rollout(game, color)
            n.backpropagate(game, reward)
        return self.root.best_child().move

    def relocate_root(self, game, move):
        for c in self.root.children:
            if c.move == move:
                self.root = c
                self.root.father = None
                self.root.move = None
        self.root = MCTS(game)
