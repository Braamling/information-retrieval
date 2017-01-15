import re

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


        self.RCP = self.calculate_RCP(self.counter_C, self.counter_D)

    """
    Returns the probability of a user clicking a doc in a Random Click Model(RCM)
    """
    def calculate_RCP(self, click_amount, docs_shown):
        return click_amount/float(docs_shown)


"""
Sample function given probability of clicking a document
"""
#TODO take this from hw1-2.py
def main():
    yandexDocs = YandexFilereader("YandexRelPredChallenge.txt")
    print vars(yandexDocs.get_document('5039'))

if __name__ == '__main__':
    main()
