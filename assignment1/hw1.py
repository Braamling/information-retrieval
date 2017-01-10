import itertools

def retrieve_pairs():
	return [(x[:5], x[5:]) for x in itertools.product((0, 1, 2), repeat=10)]


def main():
	print retrieve_pairs()

if __name__ == '__main__':
	main()