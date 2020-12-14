import gnugoPlayer
import Goban
import json

def play_a_game(player1, player2):
    player1.newGame(Goban.Board._BLACK)
    player2.newGame(Goban.Board._WHITE)
    players = [player1, player2]

    b = Goban.Board()
    nextplayer = 0
    nextplayercolor = Goban.Board._BLACK
    wrongmovefrom = 0

    states = list()
    actions = list()

    while not b.is_game_over():
        # save the board as state
        states.append(b._board)
        legals = b.legal_moves()
        otherplayer = (nextplayer + 1) % 2
        othercolor = Goban.Board.flip(nextplayercolor)
        move = players[nextplayer].getPlayerMove()
        # save the move as chosen action
        actions.append(Goban.Board.name_to_flat(move))
        if not Goban.Board.name_to_flat(move) in legals:
            print(otherplayer, nextplayer, nextplayercolor)
            print("Problem: illegal move")
            wrongmovefrom = nextplayercolor
            break
        b.push(Goban.Board.name_to_flat(move))
        players[otherplayer].playOpponentMove(move)
        nextplayer = otherplayer
        nextplayercolor = othercolor
    [p.endGame(None) for p in players]

    result = b.result()
    winner = -1
    if wrongmovefrom > 0:
        if wrongmovefrom == b._WHITE: winner = 0
        elif wrongmovefrom == b._BLACK: winner = 1
        else: print("ERROR")
    elif result == "1-0": winner = 1
    elif result == "0-1": winner = 0
    else: print("DEUCE")

    # give reward
    rewards = [(-1)**(n+winner) for n in range(len(actions))]
    return states, actions, rewards

################################################################################
N_GAME = 5000

data = list()
for i in range(N_GAME):
    player1 = gnugoPlayer.myPlayer()
    player2 = gnugoPlayer.myPlayer()
    states, actions, rewards = play_a_game(player1, player2)
    for s, a, r in zip(states, actions, rewards):
        data.append({'state': s.tolist(), 'action': a, 'reward': r})
    if i % (N_GAME/100) == 0:
        print('.', end='', flush=True) # avancement


# save data
print() # pour remettre proprement à la ligne :)
print(f"{len(data)} plateaux joués sur {N_GAME} parties")
with open('data/experience-replay.json', 'w') as outfile:
    json.dump(data, outfile)


# states: liste des plateaux sous forme de int[81] avec 0=vide, 1=noir, 2=blanc
# actions: liste des coups entre 0 et 81 (81=PASS)
# rewards: 1 pour tous les coups du vainqueur, -1 sinon
