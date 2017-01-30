from LambdaRankHW import LambdaRankHW, POINTWISE, PAIRWISE, LISTWISE
from query import load_queries
import logging
import numpy as np


class Config():
    FEATURE_COUNT = 64
    FOLDS = 1
    NUM_EPOCHS = 1
    NUM_SUB_EPOCHS = 20

""" Train a certain set of configurations with a given rank type """
def train_configuration(config, rank_type=PAIRWISE):
    # Perform this amount of folds configured.
    for i in range(1, config.FOLDS + 1):
        # Create the lambda rank object for training
        lambdaRank = LambdaRankHW(config.FEATURE_COUNT, rank_type)
        
        train_queries = load_queries('./HP2003/Fold' + str(i) + '/train.txt', config.FEATURE_COUNT)
        valid_queries = load_queries('./HP2003/Fold' + str(i) + '/vali.txt', config.FEATURE_COUNT)
        test_queries = load_queries('./HP2003/Fold' + str(i) + '/test.txt', config.FEATURE_COUNT)
        
        for j in range(config.NUM_EPOCHS):
            lambdaRank.train_with_queries(train_queries, config.NUM_SUB_EPOCHS, valid_queries)
            # lambdaRank.train_with_queries(valid_queries, config.NUM_SUB_EPOCHS)

        ndcg = lambdaRank.ndcgs(test_queries, 10)
        print ndcg
        print "The average ndcg is: " + str(np.average(ndcg))

def main():
    config = Config()
    logging.basicConfig(filename='debug.log',level=logging.DEBUG)

    # Train all three types of rank types
    # train_configuration(config, rank_type=POINTWISE)
    # train_configuration(config, rank_type=PAIRWISE)
    train_configuration(config, rank_type=LISTWISE)


if __name__ == '__main__':
    main()