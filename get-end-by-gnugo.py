from GnuGo import *
import numpy as np
#board = Board()
#board.prettyPrint()
#for m in "D4 E4 D3 E5 E6 E7 D2 F6 G7 D6 B2 F5 B3 G5 C2 G6 C3".split():
#    print([Board.coordToName(m) for m in board.legalMoves()])
#    board.playNamedMove(m.strip())
#    board.prettyPrint()
#    print(board)

#import sys
#sys.exit()
def name_to_coord(s):
    assert s != "PASS"
    indexLetters = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6, 'H':7, 'J':8}

    col = indexLetters[s[0]]
    lin = int(s[1:]) - 1
    return col, lin
def monte_carlo(gnugo, moves, nbsamples = 100):

    list_of_moves = [] # moves to backtrack
    #if len(moves) > 1 and moves[-1] == "PASS" and moves[-2] == "PASS":
    #    return None # FIXME
    epochs = 0 # Number of played games
    toret = []
    black_wins = 0
    white_wins = 0
    black_points = 0
    white_points = 0
    nb_victoryB = np.zeros((9,9))
    nb_victoryW = np.zeros((9,9))
    nb_seen = np.zeros((9,9))
    probaB = np.zeros((9,9))
    probaW = np.zeros((9,9))
    while epochs < nbsamples:
        #print(epochs)
        isfirstmove = True
        while True:
            m = moves.get_randomized_best()
            #print(epochs, m)
            if isfirstmove:
                firstmove = m
                isfirstmove = False
            r = moves.playthis(m)
            if r == "RES":
                return None
            list_of_moves.append(m)
            if len(list_of_moves) > 1 and list_of_moves[-1] == "PASS" and list_of_moves[-2] == "PASS":
                break
        if firstmove != "PASS":
            nb_seen[name_to_coord(firstmove)] += 1
        score = gnugo.finalScore()
        toret.append(score)
        if score[0] == "W":
            white_wins += 1
            if firstmove != "PASS":
                nb_victoryW[name_to_coord(firstmove)] += 1
            if score[1] == "+":
                white_points += float(score[2:])
        elif score[0] == "B":
            black_wins += 1
            if firstmove != "PASS":
                nb_victoryB[name_to_coord(firstmove)] += 1
            if score[1] == "+":
                black_points += float(score[2:])
        (ok, res) = gnugo.query("gg-undo " + str(len(list_of_moves)))
        list_of_moves = []
        epochs += 1
    probaB = np.divide(nb_victoryB, nb_seen,out=np.zeros_like(nb_victoryB), where=nb_seen!=0)
    probaW = np.divide(nb_victoryW, nb_seen,out=np.zeros_like(nb_victoryW), where=nb_seen!=0)
    print(probaB)
    print(probaW)
    return epochs, toret, black_wins, white_wins, black_points, white_points

def doit():
#(ok, _) = gnugo.query("set_random_seed 1234")
#assert ok=='OK'
#board.prettyPrint()
    gnugo = GnuGo(9)
    moves = gnugo.Moves(gnugo)
    depth = 0
    list_of_moves = []
    while True: #not board.is_game_over():
        #print("Legal Moves for player " +Board.player_name(board._nextPlayer))
        (ok, legal) = gnugo.query("all_legal " + moves.player())
        if len(legal) == 0:
            break
        #print("GNUGO", legal[1:])
        #move = moves.getbest()
        move = moves.get_randomized_best()
        depth += 1
        #print("..", move)
        retvalue = moves.playthis(move)
        if retvalue == "ERR": break
        #board.push(Board.name_to_flat(move))
        #board.prettyPrint()
        list_of_moves.append(move)
        if len(list_of_moves) > 1 and list_of_moves[-1] == "PASS" and list_of_moves[-2] == "PASS":
            break

    backtrack = random.randint(5, len(list_of_moves)-5)
#print("The game was", len(list_of_moves), "long, let's get back", backtrack, "levels to some previous position for monte carlo...")
    (ok, res) = gnugo.query("gg-undo " + str(backtrack))
    list_of_moves = list_of_moves[:-backtrack]

    (ok, blackstones) = gnugo.query('list_stones black')
    blackstones = blackstones.strip().split()
    (ok, whitestones) = gnugo.query('list_stones white')
    whitestones = whitestones.strip().split()

    (epochs, scores, black_wins, white_wins, black_points, white_points) = monte_carlo(gnugo, moves, 100)
    summary = {"depth": len(list_of_moves), "list_of_moves": list_of_moves,
            "black_stones":blackstones, "white_stones": whitestones,
            "rollouts":epochs,
            #"detailed_results": scores,
            "black_wins":black_wins, "black_points": black_points,
            "white_wins":white_wins, "white_points":white_points}
    print(summary)
    (ok, _) = gnugo.query("quit")

#print(gnugo.finalScore())
# 15 minutes max par run avant de lancer le dernier
import time
t=time.time()
while (time.time() - t < 60*60): # une heure
    doit()
