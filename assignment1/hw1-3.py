import re

class YandexFilereader():
    def __init__(self, path):
        self.path = path
        self.read_yandex_data("YandexRelPredChallenge.txt")

    """
    Read Yandex data and calculate random click probability
    """
    def read_yandex_data(self, path):
        log = []
        counter_D = 0
        counter_C = 0
        with open(paht) as f:
            content = f.readlines()
            for line in content:
                line = line.rstrip('\n')
                log.append(re.split(r'\t+', line))
                if log[-1][2] == 'Q':
                    counter_D += 10
                if log[-1][2] == 'C':
                    counter_C += 1
        RCP = self.calculate_RCP(counter_C, counter_D)
        return log, RCP

    """
    Returns the probability of a user clicking a doc in a Random Click Model(RCM)
    """
    def calculate_RCP(self, click_amount, docs_shown):
        return click_amount/float(docs_shown)


"""
Sample function given probability of clicking a document
"""
#TODO take this from hw1-2.py