import itertools

def retrieve_pairs():
	return [(x[:5], x[5:]) for x in itertools.product((0, 1, 2), repeat=10)]

def retrieve_pair():
    for x in itertools.product((0, 1, 2), repeat=10):
        yield (x[:5], x[5:])

def main():
    pair = retrieve_pair()

    for i in range(10):
        print pair.next()



if __name__ == '__main__':
	main()