import numpy as np
from tensorflow.keras.callbacks import Callback
import json
import Goban

rejected = 0
def encoder(game):
    global rejected
    board = Goban.Board()
    moves = game["list_of_moves"]
    for move in moves :
        try:
            board.push(board.flatten(board.name_to_coord(move)))
        except Exception as var:
            rejected += 1
    B = np.zeros((9, 9))
    W = np.zeros((9, 9))
    lib = [np.zeros((9,9)) for _ in range(8)]
    for x in range(9):
        for y in range(9):
            c = board._board[board.flatten((x,y))]
            if c == board._BLACK:
                B[x,y] = 1
            elif c == board._WHITE:
                W[x,y] = 1
            l = min(board._stringLiberties[board.flatten((x,y))], 3)
            lib[l][x,y] = 1
    X = [B,W] + lib
    if len(moves) % 2 == 0: X.append(np.zeros((9,9)))
    else: X.append(np.ones((9,9)))
    Y = game['black_wins'] / game['rollouts']
    return X, Y

def symetries_rotations(x):
    new = list()
    new.append(x)
    new.append([np.flipud(b) for b in new[-1]])
    new.append([np.rot90(b) for b in new[-2]])
    new.append([np.flipud(b) for b in new[-1]])
    new.append([np.rot90(b) for b in new[-2]])
    new.append([np.flipud(b) for b in new[-1]])
    new.append([np.rot90(b) for b in new[-2]])
    new.append([np.flipud(b) for b in new[-1]])
    return new

def create_all_x_y():
    global rejected
    raw_samples_file = "data/samples-9x9.json"
    with open(raw_samples_file, "r") as f:
        data = json.loads(f.read())
    X = list()
    Y = list()
    data = [encoder(d) for d in data]
    for x, y in data:
        X += symetries_rotations(x)
        Y += [y] * 8
    print(f"{rejected} parties rejetées, reste {len(Y)/8}")
    X = [np.array(x).reshape((9,9,-1)) for x in X]
    return np.array(X), np.array(Y)

class History(Callback):
    def __init__(self):
        self.history = {}
    def on_epoch_end(self, epoch, logs={}):
        for k,v in logs.items():
            if not k in self.history: self.history[k]=[]
            self.history[k].append(v)
        print(".",end="")

def print_board(b): # shape (11,9,9)
    for i in range(9):
        for j in range(9):
            if b[0][i,j] == 1:
                print('X', end=' ')
            elif b[1][i,j] == 1:
                print('O', end=' ')
            else:
                print('.', end=' ')
        print() # retour ligne

################################################################################
# tests
if __name__ == '__main__':
    create_all_x_y()
