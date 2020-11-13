# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

import time
import math
import Goban
import numpy as np
from random import choice
from playerInterface import *

start = 0 #temps initial
timeToCalculate = 3 #temps de l'iterative deepning (temps que l'on a pour faire un coup)
hasFinished = True #Booléen qui nous dis si on a fini notre recherche ou si l'iterative deepning nous en a fait sortir avant

tab5 = [0.9, 1.1, 1., 1.1, 0.9]
tab7 = [0.9, 1.1, 1.1, 1., 1.1, 1.1, 0.9]
tab9 = [0.8, 1.5, 2.5, 2, 2, 2, 2.5, 1.5, 0.8]
#analyse un bout 2*2 du plateau
def getvalue2x2(boardpiece, color):
    assert(boardpiece.shape == (2,2))
    tab = boardpiece.copy()
    c = color
    if (color == 1):
        EnnemyColor = 2
    else:
        EnnemyColor = 1
    tab = np.reshape(tab,4)
    for i in range(len(tab)):
        if tab[i] != c & tab[i] != EnnemyColor:
            tab[i] = 0
    if (tab == [EnnemyColor,c,c,c]).all() or (tab == [c,EnnemyColor,c,c]).all() or (tab == [c,c,EnnemyColor,c]).all() or (tab == [c,c,c,EnnemyColor]).all():#capture
        return 11
    if (tab == [EnnemyColor,EnnemyColor,c,c]).all() or (tab == [EnnemyColor,c,EnnemyColor,c]).all() or (tab == [c,c,EnnemyColor,EnnemyColor]).all() or (tab == [c,EnnemyColor,c,EnnemyColor]).all():#potentielle capture vers la fin si il s'agit d'un des seul degré de liberté restant
        return 5
    if (tab == [0,c,c,c]).all():#oeil
        return 6
    if (tab == [c,c,c,c]).all():
        return 1
    if (tab == [c,0,0,0]).all() or (tab == [0,c,0,0]).all() or (tab == [0,0,c,0]).all() or (tab == [0,0,0,c]).all():
        return 0
    if (tab == [c,c,c,0]).all() or (tab == [0,c,c,c]).all() or (tab == [c,0,c,c]).all() or (tab == [c,c,c,0]).all():
        return 4
    if (tab == [c,c,0,0]).all() or (tab == [0,c,c,0]).all() or (tab == [0,0,c,c]).all() or (tab == [0,c,c,0]).all():
        return 3
    if (tab == [c,0,c,0]).all() or (tab == [0,c,0,c]).all():
        return 2
    return 0
#analyse un bout 3*3 du plateau
def getvalue3x3(boardpiece, color):
    assert(boardpiece.shape == (3,3))
    tab = boardpiece.copy()
    c = color
    if (color == 1):
        EnnemyColor = 2
    else:
        EnnemyColor = 1
    res = 0
    if tab[1][1] == c:
        res = 2
    nbAdj = 0 #nb d'allié adjacent à 1,1
    nbDiag = 0 #nb d'allié diagonal à 1,1
    ennemyAdj = 0 #nb d'ennemi adjacent à 1,1
    ennemyDiag = 0 #nb d'ennemi adjacent à 1,1
    for i in range(3):
        for j in range(3):
            if tab[i][j] == c :
                if i == 1 and j == 1:
                    pass
                elif i == 1 or j == 1:
                    nbAdj +=1
                else :
                    nbDiag += 1
            if tab[i][j] == EnnemyColor :
                if i == 1 and j == 1:
                    pass
                elif i == 1 or j == 1:
                    ennemyAdj +=1
                else :
                    ennemyDiag += 1
    if tab[1][1] != c & tab[1][1] != EnnemyColor: #quand il y a des cases vide on remplie à côté
        res += 4 * nbAdj - ennemyAdj
    elif tab[1][1] == c: #quand il y a une case alliée on remplie les diag et on fait attention aux côtés
        res+= nbDiag *  4 - 2 *ennemyAdj - 2 * nbAdj
    elif tab[1][1] != EnnemyColor: #si c'est un ennemi on essaye de le capturer
        res+= 10*nbAdj - 10*ennemyDiag
    if tab[1][1] != c & tab[1][1] != EnnemyColor & nbAdj == 3:#début d'oeil
        return 12
    if tab[1][1] != c & tab[1][1] != EnnemyColor & nbAdj == 4:#début d'oeil
        return 15
    if tab[1][1] == c & nbAdj >= 4 & ennemyAdj >= 1:#enlever les degré de liberté ennemi voisins au soit même
        return 16
    if tab[1][1] != c &nbAdj == 4 & nbDiag == 3:#un oeil de base
        return 20
    if tab[1][1] == EnnemyColor & nbAdj == 4:#capture
        return 26

    if tab[1][1] != c & tab[1][1] != EnnemyColor & ennemyAdj == 3:#début d'oeil adverse
        return -5
    if tab[1][1] != EnnemyColor & ennemyAdj == 4 & ennemyDiag == 3:#un oeil de base adverse
        return -10
    if tab[1][1] == c & ennemyAdj == 4:#capture adverse
        return -11
    return res

#calcule de la valeur d'un sous plateau avec getvalue2x2 et getvalue3x3
#2x2 est utilisé sur lesb ords et 3x3 est utilisé sur le reste
def getvalue(board, size, i, j, isBlack):
    value = 0
    if i == 0 and j == 0:
        value += getvalue2x2(board[0:2,0:2], 1 if isBlack else 2)
        value -= getvalue2x2(board[0:2,0:2], 2 if isBlack else 1)
    elif i == size-1 and j == size-1:
        value += getvalue2x2(board[size-2:size,size-2:size], 1 if isBlack else 2)
        value -= getvalue2x2(board[size-2:size,size-2:size], 2 if isBlack else 1)
    elif i == 0 and j == size-1:
        value += getvalue2x2(board[0:2,size-2:size], 1 if isBlack else 2)
        value -= getvalue2x2(board[0:2,size-2:size], 2 if isBlack else 1)
    elif i == size-1 and j == 0:
        value += getvalue2x2(board[size-2:size,0:2], 1 if isBlack else 2)
        value -= getvalue2x2(board[size-2:size,0:2], 2 if isBlack else 1)
    elif i == 0 or i == size-1:
        pass
    elif j == 0 or j == size-1:
        pass
    else :
        value += getvalue3x3(board[i-1:i+2,j-1:j+2], 1 if isBlack else 2)
    return value if isBlack else -value
#parcours le plateau est calcul la valeur des sous plateaux
def evaluate(b, isBlack):
    score = 0.
    size = Goban.Board._BOARDSIZE
    board = (b._board.copy())
    board = np.resize(board, (size,size))
    encodetab = { 5:tab5, 7:tab7, 9:tab9}

    for i in range(size):
        for j in range(size):
            if board[i][j] == 1:
                score += (encodetab[size])[i] * (encodetab[size])[j]
                score += getvalue(board, size, i, j, isBlack)
            if board[i][j] == 2:
                score -= (encodetab[size])[i] * (encodetab[size])[j]
                score -= getvalue(board, size, i, j, isBlack)
    return score if isBlack else -score

lastmove = None
#Negamax alpha beta
def NegAlphaBeta(b,profondeur,profondeurMax,alpha,beta, isBlack): #b the board, prodondeur la profendeur actuelle,profondeurmax la maximale, MinorMax bool -1 pour min, 1 pour Max
    global lastmove
    b1 = b
    if (b1.is_game_over() or profondeur == profondeurMax):
        return (evaluate(b1, isBlack), lastmove) #b1.peek()
    value = -math.inf
    for move in b1.generate_legal_moves():
        if(((time.perf_counter() - start) >= timeToCalculate)):#vérifie si on n'a pas dépassé le temps donné par iterative deepning
            global hasFinished#si on l'a dépassé, on l'indique à la variable globale hasFinished que l'on n'a pas fini le parcours
            hasFinished = False
            #profondeur = profondeurMax #pour être sûr que le Negamax va bien s'arrêter
            return(alpha,move)
        b1.push(move)
        calculatedValue = -NegAlphaBeta(b1,profondeur + 1,profondeurMax,-beta, -alpha, isBlack)[0]#on évalue le plateau si on effectue ce move
        b1.pop()
        if value < calculatedValue:
            value = calculatedValue
            chosenmove = move
            lastmove = chosenmove
        if value > alpha:
            alpha = value
            chosenmove = move
            lastmove = chosenmove
            if alpha > beta:
                return(alpha,chosenmove)
    if value == -math.inf:#sécurité pour éviter l'erreur où il n'a rien trouvé
        return (0,-1)
    return (alpha,chosenmove)

def MinMaxAlphaBeta(b,profondeurmax, isBlack):
    global start
    start= time.perf_counter()#initialisation du temps initial du calcul du coup
    global hasFinished
    hasFinished = True
    totalTime = 0
    while (hasFinished): #tant que l'on a pas dépassé le temps (has Finished est modifié si l'on dépasse le temps dans le Negamax)
        t = time.perf_counter()
        move = NegAlphaBeta(b,0,profondeurmax,-math.inf, math.inf, isBlack)
        tIter = time.perf_counter() - t
        totalTime += tIter
        if(hasFinished):#si il a bien fini, on update la valeur de chosenmove
            chosenmove = move[1]
        profondeurmax += 1 #On continue en augmentant la profondeur
    	#print(move[0])
    #print(profondeurmax)
    return chosenmove



class myPlayer(PlayerInterface):
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!

    '''
    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None

    def getPlayerName(self):
        return "myPlayer"

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"
        moves = self._board.legal_moves() # Dont use weak_legal_moves() here!
        move = MinMaxAlphaBeta(self._board,1,self._mycolor == Goban.Board._BLACK)
        self._board.push(move)

        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.prettyPrint()
        # move is an internal representation. To communicate with the interface I need to change if to a string
        return Goban.Board.flat_to_name(move)

    def playOpponentMove(self, move):
        print("Opponent played ", move, "i.e. ", move) # New here
        #�the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move))

    def newGame(self, color):
        self._mycolor = color

        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")
