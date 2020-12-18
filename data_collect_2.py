"""
génére un fichier json avec:
{state: Vec82(board), m: Vec82(moyenne des victoires de gnugo)}
mais c'est trop long ~ 1 plateau / minute
"""


from GnuGo import *
import gnugoPlayer
import json
import Goban
from random import choice
import numpy as np

def play_from(moves):
    """
    à partir d'un plateau (sous forme de liste de coups)
    joues 1 partie au hazard et retourne le resultat
    """
    player1 = gnugoPlayer.myPlayer()
    player2 = gnugoPlayer.myPlayer()
    player1.newGame(Goban.Board._BLACK)
    player2.newGame(Goban.Board._WHITE)
    players = [player1, player2]

    b = Goban.Board()
    nextplayer = len(moves) % 2
    nextplayercolor = players[nextplayer]._mycolor

    for i in range(len(moves)):
        b.push(moves[i])
        players[0].playOpponentMove(b.flat_to_name(moves[i]))
        players[1].playOpponentMove(b.flat_to_name(moves[i]))

    while not b.is_game_over():
        legals = b.legal_moves()
        otherplayer = (nextplayer + 1) % 2
        othercolor = Goban.Board.flip(nextplayercolor)
        move = players[nextplayer].getPlayerMove()
        if not Goban.Board.name_to_flat(move) in legals:
            # illegal move
            return 0
        b.push(Goban.Board.name_to_flat(move))
        players[otherplayer].playOpponentMove(move)
        nextplayer = otherplayer
        nextplayercolor = othercolor
    [p.endGame(None) for p in players]

    result = b.result()
    if result == "1-0": return len(moves)%2 == 1
    elif result == "0-1": return len(moves)%2 == 0
    return 0


################################################################################
def collect_data():
    data = list()
    N_GAME = 3
    N_SIM = 2

    for _ in range(N_GAME):
        board = Goban.Board()
        played_moves = list()
        print("starting a game")
        i = 0
        while not board.is_game_over():
            i += 1
            print('.', end='', flush=True)
            moves = board.legal_moves()
            move = choice(moves)
            board.push(move)
            played_moves.append(move)
            # on fait les tests sur 1/3 des parties, sinon les plateaux sont trop proches
            if not board.is_game_over() and i % 3 == 0:
                # on enregistre le plateau
                b = np.copy(board._board).tolist()
                data.append({'state': b, 'm': [0]*82})
                # pour chaque coup possible à partir d'ici
                for move in board.legal_moves():
                    # on lance N parties avec gnugo
                    res = sum([play_from(played_moves+[move]) for _ in range(N_SIM)]) / N_SIM
                    # on stocke la moyenne des resultats dans le vecteur82
                    if move == -1: move = 81
                    data[-1]['m'][move] = res

    # save data
    print() # pour remettre proprement à la ligne :)
    print(f"{len(data)} plateaux joués sur {N_GAME} parties")
    with open('data/experience-replay-82-vic.json', 'w') as outfile:
        json.dump(data, outfile)


################################################################################
def symetries_rotations(x):
    new = list()
    new.append(np.array(x))
    new.append([np.flipud(b) for b in new[-1]])
    new.append([np.rot90(b) for b in new[-2]])
    new.append([np.flipud(b) for b in new[-1]])
    new.append([np.rot90(b) for b in new[-2]])
    new.append([np.flipud(b) for b in new[-1]])
    new.append([np.rot90(b) for b in new[-2]])
    new.append([np.flipud(b) for b in new[-1]])
    return new


def import_data():
    raw_samples_file = "data/experience-replay-82.json"
    with open(raw_samples_file, "r") as f:
        data = json.loads(f.read())
    X = list()
    Y = list()
    ps = list() # les PASS

    for game in data:
        B = np.zeros((9, 9))
        W = np.zeros((9, 9))
        P = np.zeros((9, 9))
        for i in range(9):
            for j in range(9):
                if game['state'][i+j*9] == 1:
                    B[i,j] = 1
                elif game['state'][i+j*9] == 2:
                    W[i,j] = 1
                P[i,j] = game['m'][i+j*9]
        X.append([B,W])
        Y.append([P])
        ps.append(game['m'][-1])

    Xs = list()
    Ys = list()
    Ps = list()
    for i in range(len(X)):
        Xs += symetries_rotations(X[i])
        Ys += symetries_rotations(Y[i])
        Ps += [ps[i]] * 8

    Xs = [np.array(x).reshape((9,9,-1)) for x in Xs]
    Ys = [np.array(y).reshape((81,)) for y in Ys]
    Ys = [np.concatenate([Ys[i], [Ps[i]]]) for i in range(len(Ys))]

    return np.array(Xs), np.array(Ys)

################################################################################

if __name__ == "__main__":
    collect_data()

    # X, Y = import_data()
    # print(X.shape)
    # print(Y.shape)
