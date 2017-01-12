import random
from collections import OrderedDict

class ProbInterleaving():

	# Provide a tuple of rankings and a tau size.
	def __init__(self, rankings, tau):
		self.rankings = rankings
		self.tau = tau
		self.denoms = []

		self.calculate_denominators(self)

	"""
	Calculate the denominator for the methods that will later determine the softmax function
	"""
	def calculate_denominator(self, ranking):
		denom = 0
		for rank in range(1, len(ranking) + 1):
			denom += 1 / (rank**self.tau)

		return denom

	"""
	Calculate the denominators for the methods that will later determine the softmax function
	"""	
	def calculate_denominators(self):
		for i in range(self.rankings):
			self.denoms[i] = self.calculate_denominator(self.rankings[i])

	def calculate_softmax(self, ranking_index):
		soft_max = []
		self.denoms[ranking_index] = self.calculate_denominator(ranking[ranking_index])
		for rank in len(self.ranking[ranking_index]):
			 soft_max.append(1 / (rank**self.tau))

		return soft_max

	"""
	Sample an index using a calculated softmax function and remove the item from the list
	"""
	def sample_from(self, softmax, ranking_index):
		rand_thresh = random.uniform(0, 1)

		for i, threshhold in enumarate(softmax):
			if threshold > rand_thresh:
				return i
			rand_thresh -= threshold


	"""
	Pop the next document and return the document and remove it from the list
	"""
	def pop_next_document(self, ranking_index):
		# Calculate the softmax of the ranking
		softmax = self.calculate_softmax(ranking_index)

		# Sample an index
		sampled_index = self.sample_from(softmax, ranking_index)

		document = self.rankings[ranking_index][sampled_index]

		del self.rankings[ranking_index][sampled_index]

		return document

	def interleave(self):
		for rankings in zip(ranking_a, ranking_b):
			# Toss a coin to decide which ranking goes first
			toss = random.randint(0, 1)
			interleaved.append(self.pop_next_document(self, toss))
			interleaved.append(self.pop_next_document(self, 1-toss))


def assign_document_ids(ranking_a, ranking_b):
	ranking_a = [(x, i) for i, x in enumerate(ranking_a)]
	ranking_b = [(x, i) for i, x in enumerate(ranking_b, len(ranking_a))]

	return ranking_a, ranking_b

def remove_document_ids(ranking_a, ranking_b):
	ranking_a = [x for x, i in ranking_a]
	ranking_b = [x for x, i in ranking_b]

	return ranking_a, ranking_b

""" 
Given two rankings, create a single ranking that can be used to assign credits later.
"""
def team_draft_interleave(ranking_a, ranking_b):
	interleaved = []

	# Random cointoss to determine ranking
	for rankings in zip(ranking_a, ranking_b):
		i = random.randint(0, 1)
		interleaved.append(rankings[i])
		interleaved.append(rankings[1-i])

	# Remove all duplicates from right to left.
	return list(OrderedDict.fromkeys(interleaved))

"""
Determine an amount of credits based on the given clicks (index in rank). 
"""
def assign_team_draft_credits(ranking_a, ranking_b, interleaved, clicks):
	credits_a = credits_b = 0
	# Count the amount of documents that were actually in the document
	for click in clicks:
		doc_id = interleaved[click]
		a = doc_id in ranking_a
		b = doc_id in ranking_b
		if a and b:
			if ranking_a.index(doc_id) > ranking_a.index(doc_id):
				credits_a += 1
			else: 
				credits_b += 1
		elif a or b:
			if a:
				credits_a += 1
			else:
				credits_b += 1

	return credits_a, credits_b
	

def main():

	# We consider two lists with document id's in desc order.
	ranking_a = [1, 2, 0, 0, 0, 0]
	ranking_b = [1, 2, 1, 2, 0]
	clicks = [1, 3, 4]
	random.shuffle(ranking_a)
	random.shuffle(ranking_b)

	ranking_a, ranking_b = assign_document_ids(ranking_a, ranking_b)

	print "Ranking a: " + str(ranking_a)
	print "Ranking b: " + str(ranking_b)

	# Create an interleaved ranking
	interleaved = team_draft_interleave(ranking_a, ranking_b)

	# Assign credits to both rankings based on a list of clicks (indices)
	assign_team_draft_credits(ranking_a, ranking_b, interleaved, clicks)
	
	ranking_a, ranking_b = remove_document_ids(ranking_a, ranking_b)

	print "Ranking a: " + str(ranking_a)
	print "Ranking b: " + str(ranking_b)
if __name__ == '__main__':
	main()