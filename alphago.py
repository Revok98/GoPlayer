import tensorflow as tf
import numpy as np
import Goban


def get_raw_data_go():
    ''' Returns the set of samples from the local file or download it if it does not exists'''
    import gzip, os.path
    import json

    raw_samples_file = "samples-9x9.json.gz"

    if not os.path.isfile(raw_samples_file):
        print("File", raw_samples_file, "not found, I am downloading it...", end="")
        import urllib.request
        urllib.request.urlretrieve ("https://www.labri.fr/perso/lsimon/ia-inge2/samples-9x9.json.gz", "samples-9x9.json.gz")
        print(" Done")

    with gzip.open("samples-9x9.json.gz") as fz:
        data = json.loads(fz.read().decode("utf-8"))
    return data

def encoder(data, len_hist):
    board = Goban.Board()
    moves = data["list_of_moves"]
    if len_hist > len(moves):
        return list() # erreur pas assez pour cette taille d'historique
    boards = list()
    for i in range(len(moves)) :
        board.push(moves[i])
        if len(moves) - i < len_hist:
            B = np.zeros((9, 9))
            W = np.zeros((9, 9))
            for x in range(9):
                for j in range(9):
                    c = board._board[board.flatten((i,j))]
                    if c == board._BLACK:
                        B[i,j] = 1
                    elif c == board._WHITE:
                        W[i,j] = 1
            boards += [B,W]
    if len(moves) % 2 == 0:
        boards.append(np.zeros((9,9)))
    else:
        boards.append(np.ones((9,9)))
    return boards

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

def reshape(x):
    return np.array(x).reshape((9,9,2*len_hist+1))

def create_all_x():
    len_hist = 7
    data = get_raw_data_go()
    all = list()
    for b in [encoder(d, 7) for d in data]:
        all += symetries_rotations(b)
    return [reshape(x) for x in all]


################################################################################
def game():
    model = tf.keras.models.load_model('model.h5')
    # 8 x conv(3,3,64) + flatten + dense?
    x = encoder(board)
    y = model.predict(x)
    moves = board.legal_moves()
    probas = softmax([y[move] for move in moves])
    # coup à jouer
    move = np.random.choice(moves, p=probas)
