from GnuGo import *
import numpy as np
import random as rd
import json
import os
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
    player_wins = 0
    nb_victory = np.zeros((9,9))
    nb_seen = np.zeros((9,9))
    proba_win = np.zeros((9,9))
    pass_seen = 0
    pass_victory = 0
    player = moves.player()
    while epochs < nbsamples:
        isfirstmove = True
        while True:
            if isfirstmove:#Pour le premier move on l'oblige à le faire de manière random pour bien explorer
                move_epoch = epochs%82
                line = (move_epoch-1)//9 + 1
                column = (move_epoch-1)%9 + 1
                if (line == 9):#On remplace I par J
                    line +=1
                if epochs % 82 == 0:
                    m = "PASS"
                else:
                    m = str(chr(ord('@')+line))+str(column)
                firstmove = m
                print(m)
                isfirstmove = False
            else:
                m = moves.get_randomized_best()
            r = moves.playthis(m)
            if r == "RES":
                return None
            list_of_moves.append(m)
            if len(list_of_moves) > 1 and list_of_moves[-1] == "PASS" and list_of_moves[-2] == "PASS":
                break
        if firstmove != "PASS":
            nb_seen[name_to_coord(firstmove)] += 1
        else:
            pass_seen += 1
        score = gnugo.finalScore()
        #toret.append(score)
        if player == "white" and score[0] == "W":
            player_wins += 1
            if firstmove != "PASS" and player == "white":
                nb_victory[name_to_coord(firstmove)] += 1
            elif firstmove == "PASS" and player == "white":
                pass_victory += 1
        elif player == "black" and score[0] == "B":
            player_wins += 1
            if firstmove != "PASS" and player == "black":
                nb_victory[name_to_coord(firstmove)] += 1
            elif firstmove == "PASS" and player == "black":
                pass_victory += 1
        (ok, res) = gnugo.query("gg-undo " + str(len(list_of_moves)))
        list_of_moves = []
        epochs += 1
    proba_win = np.divide(nb_victory, nb_seen,out=np.zeros_like(nb_victory), where=nb_seen!=0)

    if pass_seen != 0:
        proba_pass = pass_victory/pass_seen
    else:
        proba_pass = 0
    proba_win = proba_win.reshape(81).tolist()
    proba_win.append(proba_pass)
    return player_wins/epochs, proba_win,proba_pass,player #tolist parce json n'aime pas les array numpy

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

    (player_wins, proba_win, proba_pass, player) = monte_carlo(gnugo, moves, 410)
    summary = {"list_of_moves": list_of_moves,
            #"detailed_results": scores,
            "proba_win":player_wins,
            "proba_next_move":proba_win, "player":player}
    print(summary)
    with open("data/new_data.json", 'r') as outfile:
        if (os.stat("data/data.json").st_size != 0):
            data = json.load(outfile)  # deserialization
            data.append(summary)
        else:
            data = [summary]
    with open('data/new_data.json', 'w') as outfile:
        json.dump(data, outfile)
    (ok, _) = gnugo.query("quit")

#print(gnugo.finalScore())
# 15 minutes max par run avant de lancer le dernier
import time
t=time.time()
while (time.time() - t < 20*60*60): # une heure
    doit()
