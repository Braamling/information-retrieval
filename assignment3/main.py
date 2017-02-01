from LambdaRankHW import LambdaRankHW, POINTWISE, PAIRWISE, LISTWISE
from query import load_queries
import logging
import numpy as np
import matplotlib.pyplot as plt

class Config():
    FEATURE_COUNT = 64
    FOLDS = 5
    NUM_EPOCHS = 50
    NUM_SUB_EPOCHS = 1

""" Train a certain set of configurations with a given rank type """
def train_configuration(config, rank_type=PAIRWISE):
    # Perform this amount of folds configured.
    test_ndcgs = []
    train_ndcgs = np.zeros((config.NUM_EPOCHS))
    val_ndcgs = np.zeros((config.NUM_EPOCHS))
    for i in range(1, config.FOLDS + 1):
        # Create the lambda rank object for training
        lambdaRank = LambdaRankHW(config.FEATURE_COUNT, rank_type)

        train_queries = load_queries('./HP2003/Fold' + str(i) + '/train.txt', config.FEATURE_COUNT)
        valid_queries = load_queries('./HP2003/Fold' + str(i) + '/vali.txt', config.FEATURE_COUNT)
        test_queries = load_queries('./HP2003/Fold' + str(i) + '/test.txt', config.FEATURE_COUNT)
        for j in range(1, config.NUM_EPOCHS + 1):
            print("Epoch " + str(j))
            lambdaRank.train_with_queries(train_queries, config.NUM_SUB_EPOCHS)

            train_ndcg = np.average(lambdaRank.ndcgs(train_queries, 10))
            valid_ndcg = np.average(lambdaRank.ndcgs(valid_queries, 10))

            train_ndcgs[j-1] = train_ndcgs[j-1] + (train_ndcg / config.FOLDS)
            val_ndcgs[j-1] = val_ndcgs[j-1] + (valid_ndcg / config.FOLDS)

            print(" The average training ndcg is " + str(train_ndcg))
            print(" The average validation ndcg is " + str(valid_ndcg))
            # print "The average test ndcg is: " + str(test_ndcg)

        test_ndcgs.append(np.average(lambdaRank.ndcgs(test_queries, 10)))
        # lambdaRank.train_with_queries(valid_queries, config.NUM_SUB_EPOCHS)

    plot_valid(train_ndcgs, val_ndcgs, rank_type)
    return test_ndcgs
    # plot_test(test_ndcgs, np.average(test_ndcgs), rank_type)

def get_color(type):
    if type == POINTWISE:
        return ('r', 'r--')
    if type == PAIRWISE:
        return ('b', 'b--')
    if type == LISTWISE:
        return ('g', 'g--')

def plot_valid(train_ndcg, valid_ndcg, type):
    plt.figure(1)
    if type == POINTWISE:
        caption = "pointwise"
    elif type == PAIRWISE:
        caption = "pairwise"
    elif type == LISTWISE:
        caption = "listwise"

    color = get_color(type)

    plt.plot(range(1, len(train_ndcg)+ 1), train_ndcg,color[0], label = "train_set_" + caption)
    plt.plot(range(1, len(train_ndcg)+ 1), valid_ndcg, color[1], label = "val_set_" + caption)
    # plt.plot(range(1, len(train_ndcg)+ 1), np.repeat(test_ndcg, len(train_ndcg)), label = "test_set")
    plt.ylabel('ndcg@10')
    plt.xlabel('Epochs')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.title(caption)

def plot_test(pointwise, pairwise, listwise):
    plt.figure(2)
    avg_point = sum(pointwise) / float(len(pointwise))
    avg_pair = sum(pairwise) / float(len(pairwise))
    avg_list = sum(listwise) / float(len(listwise))

    pointwise.append(avg_point)
    pairwise.append(avg_pair)
    listwise.append(avg_list)

    n_groups = len(pointwise)
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.6
    opacity = 0.6
    rects1 = plt.bar(index*2, pointwise, bar_width, alpha=opacity, color='r', label='pointwise')
    rects2 = plt.bar(index*2 + bar_width, pairwise, bar_width, alpha=opacity, color='b', label='pairwise')
    rects3 = plt.bar(index*2 + bar_width*2, listwise, bar_width, alpha=opacity, color='g', label='listwise')

    plt.ylabel('ndcg@10')
    plt.title('K-Fold ndcg@10 on testset')

    plt.xticks(index*2 + bar_width*2, ('Fold1', 'Fold2', 'Fold3', 'Fold4','Fold5', 'Average'))
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

def main():
    # x =  []
    # x2 = [2, 3, 4, 3, 2]
    # x3 = [3, 4, 5, 4, 3]
    # plot_test(x, x2, x3)
    # plt.show()
    # print("done")
    # x = [1, 2, 3, 4]
    # x2 = [1.5, 2.5, 3.5, 4.5]
    # x3 = [2, 3, 4, 5]
    # y = [4, 3, 2, 1]
    # z = 2

    # plt.figure(1)
    # plot_valid(x, y, POINTWISE)
    # plot_valid(x3, x2, PAIRWISE)
    # plt.show()

    config = Config()
    logging.basicConfig(filename='debug.log',level=logging.DEBUG)

    # Train all three types of rank types


    point_test = train_configuration(config, rank_type=POINTWISE)
    print "point test done ------------------------------"
    pair_test = train_configuration(config, rank_type=PAIRWISE)
    print "pair test done ------------------------------"
    list_test = train_configuration(config, rank_type=LISTWISE)
    print "list test done ------------------------------"
    plot_test(point_test, pair_test, list_test)
    plt.show()


if __name__ == '__main__':
    main()