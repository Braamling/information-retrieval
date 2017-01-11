import random
from collections import OrderedDict

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
	# Count the amount of documents that were actually in the document
	credits_a = len([x for x in clicks if x in ranking_a])
	credits_b = len([x for x in clicks if x in ranking_b])

	return credits_a, credits_b
	

def main():

	# We consider two lists with document id's in desc order.
	ranking_a = [1, 2, 3, 4, 5, 6]
	ranking_b = [1, 2, 3, 5, 6]
	clicks = [1, 3, 4]
	random.shuffle(ranking_a)
	random.shuffle(ranking_b)

	print "Ranking a: " + str(ranking_a)
	print "Ranking b: " + str(ranking_b)

	# Create an interleaved ranking
	interleaved = team_draft_interleave(ranking_a, ranking_b)

	# Assign credits to both rankings based on a list of clicks (indices)
	assign_team_draft_credits(ranking_a, ranking_b, interleaved, clicks)

if __name__ == '__main__':
	main()