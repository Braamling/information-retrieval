import re

"""
Returns the probability of a user clicking a doc in a Random Click Model(RCM)
"""
def calculate_RCM(click_amount, docs_shown)
    print click_amount/float(docs_shown)

log = []
counter_D = 0
counter_C = 0
with open("YandexRelPredChallenge.txt") as f:
    content = f.readlines()
    for line in content:
        line = line.rstrip('\n')
        log.append(re.split(r'\t+', line))
        if log[-1][2] == 'Q':
            counter_D += 10
        if log[-1][2] == 'C':
            counter_C += 1

"""
Sample function given probability of clicking a document
"""
#TODO take this from hw1-2.py