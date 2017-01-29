from LambdaRankHW import LambdaRankHW
from query import load_queries

class Config():
	FEATURE_COUNT = 1000


def main():
	config = Config()

	# Create the lambda rank object for training
	lambdaRank = LambdaRankHW(config.FEATURE_COUNT)
	
	# Load first fold of files.
	queries = load_queries('./HP2003/Fold1/train.txt', 1000)

	lambdaRank.train_with_queries(queries, 5)



if __name__ == '__main__':
	main()