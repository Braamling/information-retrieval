import random
from collections import OrderedDict

class ProbInterleaving():

    # Provide a tuple of rankings and a tau size.
    def __init__(self, rankings, tau):
        self.rankings = self.assign_ranks(rankings)
        self.tau = tau
        self.denoms = [] # waarom slaan we dit op als dit opnieuw wordt berekend telkens?
        self.interleaved = []

        self.calculate_denominators()

    """
    Calculate the denominator for the methods that will later determine the softmax function
    """
    def calculate_denominator(self, ranking):
        denom = 0
        for doc in ranking:
            rank = doc[0]
            denom += 1.0 / (rank**self.tau)
        return denom

    """
    Calculate the denominators for all rankings that will later determine the softmax function
    denoms is a 2 x len(ranking) for two ranking lists initially. This should only be called
    once.
    """
    def calculate_denominators(self):
        for i in range(len(self.rankings)):
            self.denoms.append(self.calculate_denominator(self.rankings[i]))

    """
    Calculate the softmax function of a ranking, which is specified by the ranking index, and
    return this
    """
    def calculate_softmax(self, ranking_index):
        soft_max = []
        self.denoms[ranking_index] = self.calculate_denominator(self.rankings[ranking_index])
        for doc in self.rankings[ranking_index]:
            rank = doc[0]
            soft_max.append((1.0 / (rank ** self.tau)) / self.denoms[ranking_index])
        return soft_max

    """
    Sample an index using a calculated softmax function and remove the item from the list
    """
    def sample_from(self, softmax, ranking_index):
        rand_thresh = random.uniform(0, 1)
        for i, threshold in enumerate(softmax):
            if threshold >= rand_thresh:
                return i
            rand_thresh -= threshold


    """
    Pop the next document and return the document and remove it from the list
    """
    def retrieve_next_document(self, ranking_index):
        # Calculate the softmax of the ranking
        softmax = self.calculate_softmax(ranking_index)

        # Sample an index
        sampled_index = self.sample_from(softmax, ranking_index)

        document = self.rankings[ranking_index][sampled_index]

        del self.rankings[ranking_index][sampled_index]
        # TODO delete doc that occured in the second list as well.
        return self.remove_ranking(document)

    """
    Interleave once, between two rankings, of which at least one is not empty.
    """
    def interleave_once(self):
        #TODO make this more general ?
        rank1_is_empty = len(self.rankings[0])==0
        rank2_is_empty = len(self.rankings[1])==0

        toss = random.randint(0, 1)
        if(not rank1_is_empty and not rank2_is_empty):
            self.interleaved.append(self.retrieve_next_document(toss))
        elif (not rank1_is_empty):
            self.interleaved.append(self.retrieve_next_document(0))
        elif (not rank2_is_empty):
            self.interleaved.append(self.retrieve_next_document(1))
        else:
            assert(not rank1_is_empty or not rank1_is_empty), "At least one ranking should contain documents"

    """
    Interleave l times or until it is not possible anymore.
    """
    def interleave(self, l):
        for i in range(l):
            self.interleave_once()

    """
    Assign ranks which are fixed throughout the process.
    """
    def assign_ranks(self, rankings):
        new_rankings = []
        for ranking in rankings:
            new_rankings.append([(i, x) for i, x in enumerate(ranking, 1)])
        return new_rankings

    """
    Remove the rank of the document as this is only relevant to the softmax
    """
    def remove_ranking(self, document):
        return(document[1])


"""
Assign document ids to keep track of which document is which (though we assume they
cannot be the same in both rankings)
"""
def assign_document_ids(ranking_a, ranking_b):
    ranking_a = [(x, i) for i, x in enumerate(ranking_a)]
    ranking_b = [(x, i) for i, x in enumerate(ranking_b, len(ranking_a))]

    return ranking_a, ranking_b


"""
Remove the document ids in case you need more readability.
"""
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
        clicked_doc = interleaved[click-1]
        a = clicked_doc in ranking_a
        b = clicked_doc in ranking_b
        if a and b:
            if ranking_a.index(clicked_doc) > ranking_b.index(clicked_doc):
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

    ranking_a = ['hr', 'hr', 'n', 'n', 'n', 'n']
    ranking_b = ['r', 'hr', 'r', 'n', 'n']

    ranking_a, ranking_b = assign_document_ids(ranking_a, ranking_b)

    print "Ranking a: " + str(ranking_a)
    print "Ranking b: " + str(ranking_b)

    # prob_interleaving = ProbInterleaving((ranking_a, ranking_b), 3)
    # prob_interleaving.interleave(8)

    # Create an interleaved ranking
    # interleaved = prob_interleaving.interleaved
    interleaved = team_draft_interleave(ranking_a, ranking_b)

    # Assign credits to both rankings based on a list of clicks (indices)
    print assign_team_draft_credits(ranking_a, ranking_b, interleaved, clicks)

    # ranking_a, ranking_b = remove_document_ids(ranking_a, ranking_b)
    #
    # print "Ranking a: " + str(ranking_a)
    # print "Ranking b: " + str(ranking_b)

if __name__ == '__main__':
    main()