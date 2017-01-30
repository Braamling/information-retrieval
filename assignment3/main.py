from LambdaRankHW import LambdaRankHW, POINTWISE, PAIRWISE
from query import load_queries
import logging
import numpy as np


class Config():
    FEATURE_COUNT = 64
    FOLDS = 5


def main():
    config = Config()
    logging.basicConfig(filename='debug.log',level=logging.DEBUG)

    # Create the lambda rank object for training
    lambdaRank = LambdaRankHW(config.FEATURE_COUNT, POINTWISE)

    val_queries = load_queries('./HP2003/Fold1/vali.txt', config.FEATURE_COUNT)
    ndcg = lambdaRank.ndcg(val_queries, 10)
    print ndcg
    print np.average(ndcg)
    

    # Load first fold of files.
    queries = []
    for i in range(1, config.FOLDS + 1):
        queries.append(load_queries('./HP2003/Fold' + str(i) + '/train.txt', config.FEATURE_COUNT))
        logging.debug('Loaded %s', i)
    for i in range(config.FOLDS):
        lambdaRank.train_with_queries(queries[i], 10)

    ndcg = lambdaRank.ndcg(val_queries, 10)
    print ndcg
    print np.average(ndcg)


if __name__ == '__main__':
    main()