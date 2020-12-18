import numpy as np
import Goban


def get_raw_data_go():
    ''' Returns the set of samples from the local file'''
    import json

    raw_samples_file = "data/data.json"

    with open(raw_samples_file, "r") as f:
        data = json.loads(f.read())
    return data

rejected = 0

def encoder(data):
    global rejected
    board = Goban.Board()
    moves = data["list_of_moves"]
    boards = list()
    for i in range(len(moves)) :
        try:
            board.push(board.flatten(board.name_to_coord(moves[i])))
        except Exception as var:
            rejected += 1
            return list()
    B = np.zeros((9, 9))
    W = np.zeros((9, 9))
    lib = [np.zeros((9,9)) for _ in range(4)]
    for x in range(9):
        for y in range(9):
            c = board._board[board.flatten((x,y))]
            if c == board._BLACK:
                B[x,y] = 1
            elif c == board._WHITE:
                W[x,y] = 1
    boards += [B,W]
    if len(moves) % 2 == 0: boards.append(np.zeros((9,9)))
    else: boards.append(np.ones((9,9)))
    boards.append(np.array(data["proba_wins"]))
    boards.append(data["proba_win_pass"])
    boards.append(data["black_wins"] / 600)
    return boards

def symetries_rotations(x):
    new = list()
    new.append(x)
    # [:-1] sauf le dernier car c'est pas un board, c'est PASS
    new.append([np.flipud(b) for b in new[-1][:-2]] + [new[-1][-2:]])
    new.append([np.rot90(b) for b in new[-2][:-2]] + [new[-2][-2:]])
    new.append([np.flipud(b) for b in new[-1][:-2]] + [new[-1][-2:]])
    new.append([np.rot90(b) for b in new[-2][:-2]] + [new[-2][-2:]])
    new.append([np.flipud(b) for b in new[-1][:-2]] + [new[-1][-2:]])
    new.append([np.rot90(b) for b in new[-2][:-2]] + [new[-2][-2:]])
    new.append([np.flipud(b) for b in new[-1][:-2]] + [new[-1][-2:]])
    return new

def import_data():
    data = get_raw_data_go()
    all = list()
    tmp = [x for x in [encoder(d) for d in data] if len(x) != 0]
    print(f"{rejected} parties rejetées par le goban, reste {len(tmp)} parties")
    for b in tmp:
        all += symetries_rotations(b)
    X = [x[:-2] for x in all]
    Y = [np.concatenate((y[-2].reshape((81,)), [y[-1]])) for y in all]
    return np.array([reshape(x, len_hist) for x in X]), np.array(Y)
