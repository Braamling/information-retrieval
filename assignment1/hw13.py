import re
import random

class Document():
    def __init__(self, document_id):
        self.document_id = document_id
        self.queries = {}
        self.clicked_queries = {}
        self.last_clicked = 0

    # Add a single appearance in a query for this document
    def add_query(self, query_id):
        if query_id in self.queries:
            self.queries[query_id] += 1
        else:
            self.queries[query_id] = 1

    # Get the amount of appearances in a specific query for this document
    def get_query(self, query_id):
        if query_id in self.queries:
            return self.queries[query_id]
        else:
            return 0

    # Add a lasted clicked on this document
    def add_last_clicked(self):
        self.last_clicked += 1

    # Get the amount of times this document was clicked last
    def get_last_clicked(self):
        return self.last_clicked

    # Add a click on this document for a specific query
    def add_clicked_query(self, query_id):
        if query_id in self.clicked_queries:
            self.clicked_queries[query_id] += 1
        else:
            self.clicked_queries[query_id] = 1

    # Get the amount of time this document was clicked for a specific query.
    def get_clicked_query(self, query_id):
        if query_id in self.clicked_queries:
            return self.clicked_queries[query_id]
        else:
            return 0

class YandexFilereader():
    def __init__(self, path):
        self.path = path
        self.load_yandex_data(self.path)

    def get_document(self, document_id):
        return self.documents[document_id]

    """
    Read Yandex data and calculate random click probability
    """
    def load_yandex_data(self, path):
        self.documents = {}
        self.counter_D = 0
        self.counter_C = 0

        # The session query stores the last click on each query in the session
        session_query = {}
        # The session click stores the last query in a session for where each document occured
        session_click = {}

        log_type = ""
        log = []

        # The current query and session id that have to be stored on each line
        query_id = -1
        session_id = -1


        with open(path) as f:
            content = f.readlines()
            for line in content:
                line = line.rstrip('\n')
                log.append(re.split(r'\t+', line))
                log = log[-1]

                # Clear the session, should always happen after the log types have been compared.
                if session_id != log[0]:

                    # Add a last clicked for each document that registered the last click on a query.
                    for query_id in session_query:
                        self.documents[session_query[query_id]].add_last_clicked()
                        
                    # Empty the sessions
                    session_click = {}
                    session_query = {}

                # Update the session id
                session_id = log[0]

                # Check the type of log on the given line
                log_type = log[2]
                # Process either a query of a click
                if log_type == 'Q':
                    query_id = log[3]

                    # Add each document as a reponse to the given query.
                    for doc_id in log[5:15]:
                        if doc_id in self.documents:
                            self.documents[doc_id].add_query(query_id)
                        else:
                            self.documents[doc_id] = Document(doc_id)
                            self.documents[doc_id].add_query(query_id)

                        # Store the query id as last query id for this document
                        session_click[doc_id] = query_id

                    # Add 10 self.documents to the document counter
                    self.counter_D += 10
                if log_type == 'C':
                    # Add a click to a specific query
                    doc_id = log[3]
                    self.documents[doc_id].add_clicked_query(session_click[doc_id])

                    # Store the document id as last click for the query.
                    session_query[session_click[doc_id]] = doc_id

                    # Add 1 click to the clicked conted
                    self.counter_C += 1


        self.RCP = self.counter_C/ float(self.counter_D)

    def get_RCP(self):
        return self.RCP

class UserClickGenerator():

    def __init__(self, yandex_data = None):
        self.yandex_data = yandex_data

    """
    Calculate SDBM probability given the rank and relevance grades.
    """
    def calculate_SDBM(self, rank, ranking):
        attraction = self.get_attraction(ranking[rank-1][0])
        examination = self.get_examination(rank, ranking[:rank])
        return attraction * examination

    """
    Given a relevance grade {0, 1, 2} Divide this by 2 to get a fixed probability for the attractiveness.
    """

    def get_attraction(self, relevance):
        return relevance / 2.2

    """
    We calculate the examination according to the formula given by the book
    \epsilon_r+1 = \epsilon_r (\alpha_{u_rq}(1 - \sigma_{u_rq}) + (1 - \alpha_{u_rq}))
    The assumption has been made that  the attraction \alpha_{u_q} and \sigma_{u_q} are the same because
    this cannot be determined without document Id's and query Id's in our generated set. We return an
    examination chance of 1 for the first rank as this is assumed to always be checked.
    """

    def get_examination(self, rank, ranking_list):
        if rank == 1:
            return 1  # self.get_attraction(ranking_list[0])
        else:
            attraction_r = self.get_attraction(ranking_list[-2][0])
            temp = attraction_r * (1 - attraction_r) + (1 - attraction_r)
            return self.get_examination(rank - 1, ranking_list[:-1]) * temp

    """
    Returns the probability given the type of click model
    """

    def get_probability(self, rank, type, ranking):
        if type == "RCM":
            return self.yandex_data.get_RCP()
        elif type == "SDBM":
            return self.calculate_SDBM(rank, ranking)
        else:
            return None

    """
    Generate clicks given click probability
    """

    def generate_RCP_clicks(self, ranking, type):
        clicks = []
        for i in range(len(ranking)):
            toss = random.uniform(0, 1)
            if toss < self.get_probability(i + 1, type, ranking):
                clicks.append(1)
            else:
                clicks.append(0)
        return clicks



"""
Sample function given probability of clicking a document
"""
#TODO take this from hw1-2.py
def main():
    yandexDocs = YandexFilereader("YandexRelPredChallenge.txt")
    print vars(yandexDocs.get_document('5039'))

if __name__ == '__main__':
    main()
