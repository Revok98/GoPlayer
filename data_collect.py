"""
créer un json contenant:
[{
    states: liste des plateaux sous forme de int[81] avec 0=vide, 1=noir, 2=blanc,
    actions: liste des coups entre 0 et 81 (81=PASS),
    rewards: 1 pour tous les coups du vainqueur, -1 sinon
},
...]
"""

import gnugoPlayer
import Goban
import json
import numpy as np

def play_a_game():
    player1 = gnugoPlayer.myPlayer()
    player2 = gnugoPlayer.myPlayer()

    player1.newGame(Goban.Board._BLACK)
    player2.newGame(Goban.Board._WHITE)
    players = [player1, player2]

    b = Goban.Board()
    nextplayer = 0
    nextplayercolor = Goban.Board._BLACK

    states = list()
    actions = list()

    while not b.is_game_over():
        # save the board as state
        states.append(np.copy(b._board))
        legals = b.legal_moves()
        otherplayer = (nextplayer + 1) % 2
        othercolor = Goban.Board.flip(nextplayercolor)
        move = players[nextplayer].getPlayerMove()
        # save the move as chosen action
        actions.append(Goban.Board.name_to_flat(move))
        if not Goban.Board.name_to_flat(move) in legals:
            # illegal move
            return None, None, None
        b.push(Goban.Board.name_to_flat(move))
        players[otherplayer].playOpponentMove(move)
        nextplayer = otherplayer
        nextplayercolor = othercolor
    [p.endGame(None) for p in players]

    result = b.result()
    if result == "1-0": winner = 1
    elif result == "0-1": winner = 0
    else: winner = -1

    # give reward
    rewards = [(-1)**(n+winner) for n in range(len(actions))] if winner != -1 else [0]*len(actions)
    return states, actions, rewards

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
    raw_samples_file = "data/experience-replay-rewards.json"
    with open(raw_samples_file, "r") as f:
        data = json.loads(f.read())
    X = list()
    Y1 = list()
    ps = list() # les PASS
    Y2 = list()

    for game in data[:100000]:
        B = np.zeros((9, 9))
        W = np.zeros((9, 9))
        P = np.zeros((9, 9))
        for i in range(9):
            for j in range(9):
                if game['state'][i+j*9] == 1:
                    B[i,j] = 1
                elif game['state'][i+j*9] == 2:
                    W[i,j] = 1
        a = game['action']
        if a < 81: P[a%9, a//9] = 1
        ps.append(1 if a == 81 else 0)
        if game['player'] == 0: Player = np.zeros((9,9))
        else: Player = np.ones((9,9))
        X.append([B,W,Player])
        Y1.append([P])
        Y2.append(game['reward'])

    Xs = list()
    Ys = list()
    Ps = list()
    Y_values = list()
    for i in range(len(X)):
        Xs += symetries_rotations(X[i])
        Ys += symetries_rotations(Y1[i])
        Ps += [ps[i]] * 8
        Y_values += [Y2[i]] * 8

    Xs = [np.array(x).reshape((9,9,-1)) for x in Xs]
    Ys = [np.array(y).reshape((81,)) for y in Ys]
    Y_priors = [np.concatenate([Ys[i], [Ps[i]]]) for i in range(len(Ys))]

    return np.array(Xs), np.array(Y_priors), np.array(Y_values)

def collect_data():
    N_GAME = 5000 # c'est beaucoup...
    k = 0
    data = list()
    for i in range(N_GAME):
        states, actions, rewards = play_a_game()
        if states is not None: # si la partie est viable
            players = [m%2 for m in range(len(states))]
            for s, p, a, r in zip(states, players, actions, rewards):
                data.append({'state': s.tolist(), 'player': p,'action': a, 'reward': r})
        # avancement
        if i % (N_GAME/100) == 0:
            print('.', end='', flush=True)
            k += 1
            if k % 10 == 0: print('|', end='', flush=True) # pour compter les paquets de 10

    # save data
    print() # pour remettre proprement à la ligne :)
    print(f"{len(data)} plateaux joués sur {N_GAME} parties")
    with open('data/experience-replay-rewards.json', 'w') as outfile:
        json.dump(data, outfile)

################################################################################

if __name__ == "__main__":
    collect_data()

    # X, Y_priors, Y_values = import_data()
    # print(X.shape)
    # print(Y_priors.shape)
    # print(Y_values.shape)
