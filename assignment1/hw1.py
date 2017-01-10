import itertools
import math

def retrieve_new_pairs():
	return [(x[:5], x[5:]) for x in itertools.product((0, 1, 2), repeat=10)]

def retrieve_pair():
    for x in itertools.product((0, 1, 2), repeat=10):
        yield (x[:5], x[5:])

def calc_dcg(ranking, k=5):
	dcg = 0
	for rank, rel in enumerate(ranking[:k]):
		dcg += (2**rel - 1) / math.log(2 + rank, 2)

	return dcg

def avg_precision(p, n_rel_docs):
    avg_prec = 0
    counter = 0
    for i, rel in enumerate(p,1):
        if rel >= 1:
            counter+=1
            avg_prec += float(counter)/i
    return avg_prec/n_rel_docs

def main():
    pair = retrieve_pair()

    print avg_precision([1,0,2,1,0,1], 10)
    for i in range(10):
        print pair.next()

    new_pair = pair.next()


if __name__ == '__main__':
	main()