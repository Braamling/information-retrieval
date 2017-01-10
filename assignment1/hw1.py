import itertools
import math

def retrieve_new_pairs():
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
	for rank, rel in enumerate(ranking[:k]):
		dcg += (2**rel - 1) / math.log(2 + rank, 2)

	return dcg

def calc_RBP(ranking, theta=0.8):
    RBP = 0
    for rank, rel in enumerate(ranking,1):
        RBP += rel * theta**(rank-1) * (1-theta)
    return RBP

def main():
    pair = retrieve_pair()

    print calc_avg_precision([1,0,2,1,0,1], 10)
    for i in range(10):
        print pair.next()

    new_pair = pair.next()


if __name__ == '__main__':
	main()