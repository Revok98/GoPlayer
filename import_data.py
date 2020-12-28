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

def board_encoding(board):
    boards = list()
    B = np.zeros((9, 9))
    W = np.zeros((9, 9))
    for x in range(9):
        for y in range(9):
            c = board._board[board.flatten((x,y))]
            if c == board._BLACK:
                B[x,y] = 1
            elif c == board._WHITE:
                W[x,y] = 1
    boards += [B,W]
    if board._nextPlayer == board._BLACK: boards.append(np.zeros((9,9)))
    else: boards.append(np.ones((9,9)))
    return boards

def encoder(data):
    global rejected
    board = Goban.Board()
    moves = data["list_of_moves"]
    for i in range(len(moves)) :
        try:
            board.push(board.flatten(board.name_to_coord(moves[i])))
        except Exception as var:
            rejected += 1
            return list()
    boards = board_encoding(board)
    boards.append(np.array(data["proba_next_move"][:-1]).reshape((9,9)))
    boards.append(data["proba_next_move"][-1])
    boards.append(data["proba_win"])
    return boards

def symetries_rotations(x):
    new = list()
    new.append(x)
    # [:-1] sauf le dernier car c'est pas un board, c'est PASS
    new.append([np.flipud(b) for b in new[-1][:-2]] + new[-1][-2:])
    new.append([np.rot90(b) for b in new[-2][:-2]] + new[-2][-2:])
    new.append([np.flipud(b) for b in new[-1][:-2]] + new[-1][-2:])
    new.append([np.rot90(b) for b in new[-2][:-2]] + new[-2][-2:])
    new.append([np.flipud(b) for b in new[-1][:-2]] + new[-1][-2:])
    new.append([np.rot90(b) for b in new[-2][:-2]] + new[-2][-2:])
    new.append([np.flipud(b) for b in new[-1][:-2]] + new[-1][-2:])
    return new

def import_data():
    data = get_raw_data_go()
    all = list()
    tmp = [x for x in [encoder(d) for d in data] if len(x) != 0]
    print(f"{rejected} parties rejetées par le goban, reste {len(tmp)} parties")
    for b in tmp:
        all += symetries_rotations(b)
    X = [x[:-2] for x in all]
    Y1 = [np.concatenate((y[-3].reshape((81,)), [y[-2]])) for y in all]
    Y2 = [y[-1] for y in all]
    return np.array([np.array(x).reshape((9,9,-1)) for x in X]), np.array(Y1), np.array(Y2)

x, y1, y2 = import_data()

print(x.shape)
print(y1.shape)
print(y2.shape)
# data = list()
#
# with open("data/data.json", "r") as f:
#     tmp = json.loads(f.read())
#     for d in tmp:
#         new = dict()
#         new["list_of_moves"] = d["list_of_moves"]
#         new["proba_win"] = d["black_wins"] / d["rollouts"] if d["player"] == "black" else d["white_wins"] / d["rollouts"]
#         new["proba_next_move"] = np.array(d["proba_wins"]).reshape((81,)).tolist() + [d["proba_win_pass"]]
#         new["player"] = d["player"]
#         data.append(new)
# with open("data/data2.json", "r") as f:
#     tmp = json.loads(f.read())
#     for d in tmp:
#         new = dict()
#         new["list_of_moves"] = d["list_of_moves"]
#         new["proba_win"] = d["black_wins"] / d["rollouts"] if d["player"] == "black" else d["white_wins"] / d["rollouts"]
#         new["proba_next_move"] = np.array(d["proba_wins"]).reshape((81,)).tolist() + [d["proba_win_pass"]]
#         new["player"] = d["player"]
#         data.append(new)
# with open("data/data_1.json", "r") as f:
#     tmp = json.loads(f.read())
#     for d in tmp:
#         new = dict()
#         new["list_of_moves"] = d["list_of_moves"]
#         new["proba_win"] = d["black_wins"] / d["rollouts"] if d["player"] == "black" else d["white_wins"] / d["rollouts"]
#         new["proba_next_move"] = np.array(d["winning_proba"]).reshape((81,)).tolist() + [d["proba_win_pass"]]
#         new["player"] = d["player"]
#         data.append(new)
#
# with open("data/data_all.json", "w") as f:
#     json.dump(data, f)
