# -*- coding: utf-8 -*-

import time
import Goban
from random import randint, choice
from playerInterface import *

iterativeDeepening = True # variable pour autoriser l'iterative deepening (timeout = 10s par défaut)
startTime = 0 # variable enregistrant le temps de départ de la fonction pour l'iterative deepening
isDone = True # variable pour déterminer si la fonction a terminé ou non (dû au timeout) pour l'iterative deepening
timeout = 4 # timeout pour l'iterative deepening = 10s

######################### Useful functions #####################################

def randomMove(board):
    moves = board.legal_moves()
    return choice(moves)

############################# Heuristic ########################################

def antiPass(base_move):
    if(base_move == -1):
        return -10000
    return 0

def milieu(board,coord,color):
    sum = 0

    UFCoord = board.unflatten(coord)
    if(UFCoord[0] == 4 and UFCoord[1] == 4):
        sum += 1000

    return sum

def losanges_centre(board,UFCoord,color):
    sum = 0
    if(board[board.flatten((UFCoord[0]-1,UFCoord[1]-1))] == color): # diagonale bas-gauche
        sum += 1
    if(board[board.flatten((UFCoord[0]+1,UFCoord[1]-1))] == color): # diagonale bas-droite
        sum += 1
    if(board[board.flatten((UFCoord[0]-1,UFCoord[1]+1))] == color): # diagonale haut-gauche
        sum += 1
    if(board[board.flatten((UFCoord[0]+1,UFCoord[1]+1))] == color): # diagonale haut-droite
        sum += 1
    if(board[board.flatten((UFCoord[0]-2,UFCoord[1]))] == color): # à 2 cases à gauche
        sum += 1
    if(board[board.flatten((UFCoord[0]+2,UFCoord[1]))] == color): # à 2 cases à droite
        sum += 1
    if(board[board.flatten((UFCoord[0],UFCoord[1]-2))] == color): # à 2 cases en bas
        sum += 1
    if(board[board.flatten((UFCoord[0],UFCoord[1]+2))] == color): # à 2 cases en haut
        sum += 1
    return sum

def losanges_coin_bas_gauche(board,UFCoord,color):
    sum = 0
    if(board[board.flatten((UFCoord[0]+1,UFCoord[1]+1))] == color): # diagonale haut-droite
        sum += 1
    if(board[board.flatten((UFCoord[0],UFCoord[1]+2))] == color): # à 2 cases en haut
        sum += 1
    if(board[board.flatten((UFCoord[0]+2,UFCoord[1]))] == color): # à 2 cases à droite
        sum += 1
    return sum

def losanges_coin_haut_gauche(board,UFCoord,color):
    sum = 0
    if(board[board.flatten((UFCoord[0]+1,UFCoord[1]-1))] == color): # diagonale bas-droite
        sum += 1
    if(board[board.flatten((UFCoord[0],UFCoord[1]-2))] == color): # à 2 cases en bas
        sum += 1
    if(board[board.flatten((UFCoord[0]+2,UFCoord[1]))] == color): # à 2 cases à droite
        sum += 1
    return sum

def losanges_bord_gauche(board,UFCoord,color):
    sum = 0
    if(board[board.flatten((UFCoord[0]+1,UFCoord[1]+1))] == color): # diagonale haut-droite
        sum += 1
    if(board[board.flatten((UFCoord[0]+1,UFCoord[1]-1))] == color): # diagonale bas-droite
        sum += 1
    if(board[board.flatten((UFCoord[0],UFCoord[1]+2))] == color): # à 2 cases en haut
        sum += 1
    if(board[board.flatten((UFCoord[0],UFCoord[1]-2))] == color): # à 2 cases en bas
        sum += 1
    if(board[board.flatten((UFCoord[0]+2,UFCoord[1]))] == color): # à 2 cases à droite
        sum += 1
    return sum

def losanges_coin_bas_droite(board,UFCoord,color):
    sum = 0
    if(board[board.flatten((UFCoord[0]-1,UFCoord[1]+1))] == color): # diagonale haut-gauche
        sum += 1
    if(board[board.flatten((UFCoord[0],UFCoord[1]+2))] == color): # à 2 cases en haut
        sum += 1
    if(board[board.flatten((UFCoord[0]-2,UFCoord[1]))] == color): # à 2 cases à gauche
        sum += 1
    return sum

def losanges_coin_haut_droite(board,UFCoord,color):
    sum = 0
    if(board[board.flatten((UFCoord[0]-1,UFCoord[1]-1))] == color): # diagonale bas-gauche
        sum += 1
    if(board[board.flatten((UFCoord[0],UFCoord[1]-2))] == color): # à 2 cases en bas
        sum += 1
    if(board[board.flatten((UFCoord[0]-2,UFCoord[1]))] == color): # à 2 cases à gauche
        sum += 1
    return sum

def losanges_bord_droite(board,UFCoord,color):
    sum = 0
    if(board[board.flatten((UFCoord[0]-1,UFCoord[1]+1))] == color): # diagonale haut-gauche
        sum += 1
    if(board[board.flatten((UFCoord[0]-1,UFCoord[1]-1))] == color): # diagonale bas-gauche
        sum += 1
    if(board[board.flatten((UFCoord[0],UFCoord[1]+2))] == color): # à 2 cases en haut
        sum += 1
    if(board[board.flatten((UFCoord[0],UFCoord[1]-2))] == color): # à 2 cases en bas
        sum += 1
    if(board[board.flatten((UFCoord[0]-2,UFCoord[1]))] == color): # à 2 cases à gauche
        sum += 1
    return sum

def losanges_bord_bas(board,UFCoord,color):
    sum = 0
    if(board[board.flatten((UFCoord[0]-1,UFCoord[1]+1))] == color): # diagonale haut-gauche
        sum += 1
    if(board[board.flatten((UFCoord[0]+1,UFCoord[1]+1))] == color): # diagonale haut-droite
        sum += 1
    if(board[board.flatten((UFCoord[0]-2,UFCoord[1]))] == color): # à 2 cases à gauche
        sum += 1
    if(board[board.flatten((UFCoord[0]+2,UFCoord[1]))] == color): # à 2 cases à droite
        sum += 1
    if(board[board.flatten((UFCoord[0],UFCoord[1]+2))] == color): # à 2 cases en haut
        sum += 1
    return sum

def losanges_bord_haut(board,UFCoord,color):
    sum = 0
    if(board[board.flatten((UFCoord[0]-1,UFCoord[1]-1))] == color): # diagonale bas-gauche
        sum += 1
    if(board[board.flatten((UFCoord[0]+1,UFCoord[1]-1))] == color): # diagonale bas-droite
        sum += 1
    if(board[board.flatten((UFCoord[0]-2,UFCoord[1]))] == color): # à 2 cases à gauche
        sum += 1
    if(board[board.flatten((UFCoord[0]+2,UFCoord[1]))] == color): # à 2 cases à droite
        sum += 1
    if(board[board.flatten((UFCoord[0],UFCoord[1]-2))] == color): # à 2 cases en bas
        sum += 1
    return sum

def losanges(board,coord,color):
    sum = 0

    ## diagonale
    UFCoord = board.unflatten(coord)
    if(UFCoord[0] > 1 and UFCoord[1] > 1 and UFCoord[0] < 7 and UFCoord[1] < 7):
        sum = losanges_centre(board,UFCoord,color)
    elif(UFCoord[0] == 0 or UFCoord[0] == 1):
        if(UFCoord[1] == 0 or UFCoord[1] == 1):
            sum = losanges_coin_bas_gauche(board,UFCoord,color)
        elif(UFCoord[1] == 8 or UFCoord[1] == 7):
            sum = losanges_coin_haut_gauche(board,UFCoord,color)
        else:
            sum = losanges_bord_gauche(board,UFCoord,color)
    elif(UFCoord[0] == 8 or UFCoord[0] == 7):
        if(UFCoord[1] == 0 or UFCoord[1] == 1):
            sum = losanges_coin_bas_droite(board,UFCoord,color)
        elif(UFCoord[1] == 8 or UFCoord[1] == 7):
            sum = losanges_coin_haut_droite(board,UFCoord,color)
        else:
            sum = losanges_bord_droite(board,UFCoord,color)
    elif(UFCoord[1] == 0 or UFCoord[1] == 1):
        sum = losanges_bord_bas(board,UFCoord,color)
    elif(UFCoord[1] == 7 or UFCoord[1] == 8):
        sum = losanges_bord_haut(board,UFCoord,color)

    return sum

def heuristic(board,color,base_move):
    score = 0

    for coord in range(0,80):
        if(board[coord] == color):
            score += losanges(board,coord,color)
            score += milieu(board,coord,color)

    if(color == 1): #White
        score += (board._capturedWHITE - board._capturedBLACK) * 1000
    else: #Black
        score += (board._capturedBLACK - board._capturedWHITE) * 1000
    return score

def heuristicResult(b,base_move,color):
    return (heuristic(b,color,base_move), base_move)

############################## alphaBeta ##########################################

def minAlphaBeta(b,alpha,beta,depth,base_move,color):
    if (b.is_game_over() or depth <= 0):
        return(heuristicResult(b,base_move,color))

    res_min = 9999
    move_min = randomMove(b)
    for move in b.legal_moves():
        if(((time.perf_counter() - startTime) >= timeout) and iterativeDeepening):
            global isDone
            isDone = False
            print("timeout ! returning ...")
            return(res_min, move_min)
        b.push(move)
        res = maxAlphaBeta(b,alpha,beta,depth-1,move,color)
        b.pop()
        if(res[0]<res_min):
            res_min = res[0]
            move_min = move
        if(alpha >= res[0]):
            return (res_min, move_min)
        beta = min(beta,res[0])
    return (res_min, move_min)

def maxAlphaBeta(b,alpha,beta,depth,base_move,color):
    if (b.is_game_over() or depth <= 0):
        return(heuristicResult(b,base_move,color))

    res_max = 0
    move_max = randomMove(b)
    for move in b.legal_moves():
        if(((time.perf_counter() - startTime) >= timeout) and iterativeDeepening):
            global isDone
            isDone = False
            print("timeout ! returning ...")
            return(res_max, move_max)
        b.push(move)
        res = minAlphaBeta(b,alpha,beta,depth-1,move,color)
        b.pop()
        if(res[0]>res_max):
            res_max = res[0]
            move_max = move
        if(res[0] >= beta):
            return (res_max, move_max)
        alpha = max(alpha,res[0])
    return (res_max, move_max)

def iterativeDeepeningMove(b,color):
    depth = 1
    global startTime
    startTime = time.perf_counter()
    global iterativeDeepening
    iterativeDeepening = True
    global isDone
    isDone = True
    t_total = 0
    res = randomMove(b)
    while(isDone):
        t = time.perf_counter()
        temp_res = maxAlphaBeta(b,-9999,9999,depth,randomMove(b),color)
        tt = time.perf_counter() - t
        t_total += tt
        if(isDone):
            res = temp_res
        print("time = {}; depth = {}; isDone = {}".format(t_total,depth,isDone))
        depth += 1
    return res[1]

class myPlayer(PlayerInterface):
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!

    '''

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None

    def getPlayerName(self):
        return "MinMax3 Player"

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"
        # moves = self._board.legal_moves() # Dont use weak_legal_moves() here!
        move = iterativeDeepeningMove(self._board,self._mycolor)
        self._board.push(move)

        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.prettyPrint()
        # move is an internal representation. To communicate with the interface I need to change if to a string
        return Goban.Board.flat_to_name(move)

    def playOpponentMove(self, move):
        print("Opponent played ", move, "i.e. ", move) # New here
        # the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move))

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")
