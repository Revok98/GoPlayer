import numpy as np
import Goban
import json


def get_raw_data_go():
    ''' Returns the set of samples from the local file'''
    raw_samples_file = "data/data.json"
    with open(raw_samples_file, "r") as f:
        data = json.loads(f.read())
    return data

rejected = 0

def board_encoding(board, liberties=0):
    boards = np.zeros((9,9,3+liberties))
    for x in range(9):
        for y in range(9):
            c = board._board[board.flatten((x,y))]
            if c == board._BLACK:
                boards[x,y,0] = 1
            elif c == board._WHITE:
                boards[x,y,1] = 1
            if liberties > 0:
                l = min(board._stringLiberties[board.flatten((x,y))], liberties-1)
                boards[x,y,l+2] = 1
    if board._nextPlayer != board._BLACK:
        boards[:,:,-1] = 1
    return boards

def encoder(data, h=5, liberties=0):
    global rejected
    board = Goban.Board()
    moves = data["list_of_moves"]
    if len(moves) < h:
        return None
    b = np.zeros((9,9,h*(2+liberties)+1))
    for i in range(len(moves)) :
        try:
            board.push(board.flatten(board.name_to_coord(moves[i])))
        except Exception as var:
            rejected += 1
            return None
        if i >= len(moves) - h:
            tmp = board_encoding(board, liberties)
            b[:,:,(2+liberties)*(i-len(moves)+h):(2+liberties)*(i-len(moves)+h+1)] = tmp[:,:,:2+liberties]
    if len(moves) % 2 == 1:
        b[:,:,-1] = 1
    #boards = board_encoding(board)
    proba_move = np.array(data["proba_next_move"][:-1]).reshape((9,9))
    proba_pass = data["proba_next_move"][-1]
    proba_win = 2 * data["proba_win"] - 1
    return b, proba_move, proba_pass, proba_win

def symetries_rotations(x):
    # input (9,9,k)
    new = list()
    new.append(x)
    new.append(np.flipud(new[-1]))
    new.append(np.rot90(new[-2]))
    new.append(np.flipud(new[-1]))
    new.append(np.rot90(new[-2]))
    new.append(np.flipud(new[-1]))
    new.append(np.rot90(new[-2]))
    new.append(np.flipud(new[-1]))
    return new

def import_data(historique=0, liberties=0):
    data = get_raw_data_go()
    all = list()
    tmp = [x for x in [encoder(d, historique, liberties) for d in data] if x is not None]
    print(f"{rejected} parties rejetées par le goban, reste {len(tmp)} parties")
    X = list()
    Y1 = list()
    Y2 = list()
    for b, m, p, w in tmp:
        X += symetries_rotations(b)
        for t in symetries_rotations(m):
            Y1.append(np.concatenate([np.array(t).reshape((81,)), [p]]))
        Y2 += [w] * 8
    return np.array(X), np.array(Y1), np.array(Y2)

# x, y1, y2 = import_data()
# print(x.shape)
# print(y1.shape)
# print(y2.shape)

# data = list()
# with open("data/new_data.json", "r") as f:
#     data = json.loads(f.read())
# with open("data/old_data.json", "r") as f:
#     data += json.loads(f.read())
# with open("data/data.json", "w") as f:
#     json.dump(data, f)
