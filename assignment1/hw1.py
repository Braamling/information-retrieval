import itertools
import math

def retrieve_pairs():
	return [(x[:5], x[5:]) for x in itertools.product((0, 1, 2), repeat=10)]

# This function returns an iterator which returns a unique ranking of P and E for each iteration
def retrieve_pair():
    for x in itertools.product((0, 1, 2), repeat=10):
        yield (x[:5], x[5:])

def calc_recall(ranking, n_rel_docs, k=5):
    counter = 0
    for rel in ranking[:k]:
        if rel >= 1:
            counter+=1
    return float(counter)/n_rel_docs

# This function calculates the precision at rank k, k needs to be smaller than the ranking size.
def calc_precision(ranking, k=5):
    assert k<len(ranking), "k needs to be smaller than the amount of documents"
    counter = 0
    for rank, rel in enumerate(ranking[:k], i):
        if rel >=1:
            counter += 1
    return counter/k


def calc_avg_precision(ranking, n_rel_docs):
    avg_prec = 0
    counter = 0
    for rank, rel in enumerate(ranking,1):
        if rel >= 1:
            counter+=1
            avg_prec += float(counter)/rank
    return avg_prec/n_rel_docs

def calc_dcg(ranking, k=5):
	dcg = 0
	# Iterate over each position in the ranking until at position k
	for rank, rel in enumerate(ranking[:k], 1):
		# Calculate the dg of the current rank an dadd it to the sum of the dcg.
		dcg += (2**rel - 1) / math.log(1 + rank, 2)

	return dcg

def calc_RBP(ranking, theta=0.8):
    RBP = 0
    for rank, rel in enumerate(ranking,1):
        RBP += rel * theta**(rank-1) * (1-theta)
    return RBP

def normalized_dcg(ranking, k=5):
	# Calculate the unnormalized dcg of the ranking up to point k
	dcg = calc_dcg(ranking, k)

	# Create the best ranking and calculate its dcg over the whole ranking.
	best_rank = sorted(ranking, reverse=True) 
	best_dcg = calc_dcg(best_rank, len(best_rank))

	# Prevent devision by zero
	if best_dcg == 0.0:
		return 1.0

	# Normalize the dcg
	return dcg/best_dcg

"""
Calculate all implemented scores for a specific ranking
"""
def calculate_scores(ranking):
	results = {}
	results['dcg'] = calc_dcg(ranking, len(ranking))
	results['ndcg'] = normalized_dcg(ranking, len(ranking))
	results['rbp'] = calc_RBP(ranking)
	results['ndcg'] = normalized_dcg(ranking, len(ranking))
	results['recall'] = calc_recall(ranking, 5, len(ranking))
	results['precision'] = calc_precision(ranking, len(ranking))
	results['avg_precision'] = calc_avg_precision(ranking, 5)

	return results

def calculate_measure(pair):
	# ITerate over all scoring types and calculate the measurements
	measures = ['dcg', 'ndcg', 'rbp', 'ndcg', 'recall', 'precision', 'avg_precision']

	# Calculate both scores
	results_p = calculate_scores(pair[0])
	results_e = calculate_scores(pair[1])

	results = {}

	for measurement in measures:
		# If any of the measurements is negative, the results are discarded. 
		result = results_p[measurement] - results_e[measurement]
		if result < 0:
			return None

		# Add the measurement to the results
		results[measurement] = result

	return results

def main():
    pairs = retrieve_pairs()

    # Check the measurements for each pair
    for pair in pairs:
    	measure = calculate_measure(pair)

    	# Ignore the pair if result_e < result_p
    	if measure is not None:
	    	print measure


if __name__ == '__main__':
	main()