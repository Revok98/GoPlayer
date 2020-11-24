import numpy as np
import Goban


def get_raw_data_go():
    ''' Returns the set of samples from the local file'''
    import json

    raw_samples_file = "data.json"

    with open(raw_samples_file, "r") as f:
        data = json.loads(f.read())
    return data

rejected = 0

def encoder(data, len_hist):
    global rejected
    board = Goban.Board()
    moves = data["list_of_moves"]
    if len_hist > len(moves):
        return list() # erreur pas assez pour cette taille d'historique
    boards = list()
    for i in range(len(moves)) :
        try:
            board.push(board.flatten(board.name_to_coord(moves[i])))
        except Exception as var:
            rejected += 1
            return list()
        if len(moves) - i <= len_hist:
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
    if len(moves) % 2 == 0:
        boards.append(np.zeros((9,9)))
    else:
        boards.append(np.ones((9,9)))
    boards.append(np.array(data["proba_wins"]))
    boards.append(data["proba_win_pass"])
    return boards

def symetries_rotations(x):
    new = list()
    new.append(x)
    # [:-1] sauf le dernier car c'est pas un board, c'est PASS
    new.append([np.flipud(b) for b in new[-1][:-1]] + [new[-1][-1]])
    new.append([np.rot90(b) for b in new[-2][:-1]] + [new[-2][-1]])
    new.append([np.flipud(b) for b in new[-1][:-1]] + [new[-1][-1]])
    new.append([np.rot90(b) for b in new[-2][:-1]] + [new[-2][-1]])
    new.append([np.flipud(b) for b in new[-1][:-1]] + [new[-1][-1]])
    new.append([np.rot90(b) for b in new[-2][:-1]] + [new[-2][-1]])
    new.append([np.flipud(b) for b in new[-1][:-1]] + [new[-1][-1]])
    return new

def reshape(x, len_hist):
    return np.array(x).reshape((9,9,2*len_hist+1))

def create_all_x_y():
    len_hist = 7
    data = get_raw_data_go()
    all = list()
    tmp = [x for x in [encoder(d, 7) for d in data] if len(x) != 0]
    print(f"{rejected} parties rejetées par le goban, reste {len(tmp)} parties")
    for b in tmp:
        all += symetries_rotations(b)
    X = [x[:-2] for x in all]
    Y = [np.concatenate((y[-2].reshape((81,)), [y[-1]])) for y in all]
    return np.array([reshape(x, len_hist) for x in X]), np.array(Y)

################################################################################
# def game():
#     import tensorflow as tf
#     model = tf.keras.models.load_model('model.h5')
#     # 8 x conv(3,3,64) + flatten + dense?
#     x = encoder(board)
#     y = model.predict(x)
#     moves = board.legal_moves()
#     probas = softmax([y[move] for move in moves])
#     # coup à jouer
#     move = np.random.choice(moves, p=probas)
