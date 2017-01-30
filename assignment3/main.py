from LambdaRankHW import LambdaRankHW, POINTWISE, PAIRWISE
from query import load_queries

class Config():
	FEATURE_COUNT = 64


def main():
	config = Config()

	# Create the lambda rank object for training
	lambdaRank = LambdaRankHW(config.FEATURE_COUNT, POINTWISE)
	
	# Load first fold of files.
	queries = load_queries('./HP2003/Fold1/train.txt', config.FEATURE_COUNT)

	lambdaRank.train_with_queries(queries, 5)



if __name__ == '__main__':
	main()