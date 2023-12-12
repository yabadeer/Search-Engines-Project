# Provided by Professor Smucker - not written myself
from collections import defaultdict

class Result:
    def __init__(self, doc_id, score, rank):
        self.doc_id = doc_id
        self.score = score
        self.rank = rank

    def __lt__(self, x):
        return (self.score, self.doc_id) > (x.score, x.doc_id)

class Results:
    def __init__(self):
        self.query_2_results = defaultdict(list)

    def add_result(self, query_id, result):
        self.query_2_results[query_id].append(result)

    def get_result(self, query_id):
        return self.query_2_results.get(query_id, None)

