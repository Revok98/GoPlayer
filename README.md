# AlphaGo

AlphaGo-nn-priors-values-gnugo.ipynb: sert à initialiser les réseaux des neurones en les entrainant sur des parties de gnugo

AlphaGo_Reinforcement_Learning.ipynb: Reprend les principes du RL pour entrainer le joueur en jouant contre lui-même (trop long pour atteindre des résultats probant mais la théorie est là)

mcts.py: implémentation de la méthode de monte carlo

mctsPlayer.py: joueur utilisant la méthode de monte carlo, capable de battre un joueur random mais prend du temps à jouer

mctsNN.py: modification du monte carlo avec les réseaux de neurones d'AlphaGo

mctsPlayerNN.py: joueur qui imite AlphaGo, entrainé contre lui-même dans le notebook précédent, mais le manque de temps fait qu'il est très peu performant et se fait battre par un joueur aléatoire car il a tendance à regrouper ces pions, se les faisant donc prendre facilement.

get-end-by-gnugo.py: permet de générer les data pour préentrainer les réseaux de neurones.

import_data.py: permet d'importer les données créées avec gnugo depuis leur fichier json afin d'entrainer les réseaux de neurones.

data_collect.py: n'est plus utilisé, servait à la base à généré de l'experience replay avec gnugo; remplacé par le notebook de RL.
