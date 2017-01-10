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


def main():
    pair = retrieve_pair()

    for i in range(10):
        print pair.next()

    new_pair = pair.next()


if __name__ == '__main__':
	main()