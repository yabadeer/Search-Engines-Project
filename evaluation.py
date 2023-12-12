'''
Acknowledgements:
- I relied on code provided by the prof. I utilized import statements to use the classes provided.
- Used Chat GPT to help me implement the math for ndcg (told me about the import math statement and functionality)
- Will provide URLs for all links that are worth crediting and referencing.
- I collaborated with Inesh Jacob on some of the concepts of this assignment (mainly DCG).
'''

# import statements 
import sys # user input
import math # math operations
from parsers import QrelsParser, ResultsParser # prof provided code

def calculatePrecisionAtK(queryId, retrievedDocs, qrels, k):
    """
    Calculate the precision at rank k for search results.
    
    retrievedDocs: list of Result objects that were retrieved, sorted by score descending
    qrels: Qrels object containing all judgements
    k: rank at which to calculate precision
    return: precision at rank k score as a float
    """
    if len(retrievedDocs) < k:
        k = len(retrievedDocs)
    topKRetrieved = retrievedDocs[:k]
    numRelevant = 0

    for result in topKRetrieved:
        relevance = qrels.get_relevance(queryId, result.doc_id)
        if relevance > 0:  # Assuming that a relevance score greater than 0 indicates binary relevance
            numRelevant += 1

    precisionAtK = numRelevant / k if k > 0 else 0
    return precisionAtK

def calculateAveragePrecision(queryId, retrievedDocs, qrels):
    """
    Calculate the average precision for search results.
    
    retrievedDocs: list of Result objects that were retrieved, sorted by score descending
    qrels: Qrels object containing all judgements
    query_id: the query ID for which to calculate precision
    return: average precision score as a float
    """
    
    numRelevant = 0
    sumPrecision = 0.0
    for i, result in enumerate(retrievedDocs):
        relevance = qrels.get_relevance(queryId, result.doc_id)
        if relevance > 0:  # Assuming that a relevance score greater than 0 indicates relevance
            numRelevant += 1
            precisionAtI = numRelevant / (i + 1)  # Precision at this rank position i
            sumPrecision += precisionAtI

    # If there are no relevant documents, average precision is undefined (or zero)
    # averagePrecision = sumPrecision / numRelevant if numRelevant > 0 else 0 # this was working until I realized the logic error
    averagePrecision = sumPrecision/float(len(qrels.query_2_reldoc_nos[queryId]))
    return averagePrecision

# Function to calculate DCG
def calculateDcgAtK(queryId, retrievedDocs, qrels, k):
    dcg = 0.0
    # Adjust k to the length of retrievedDocs if necessary
    k = min(k, len(retrievedDocs))
    for i, doc in enumerate(retrievedDocs[:k], start=1):
        relevance = qrels.get_relevance(queryId, doc.doc_id)  # passing both queryId and doc_id
        gain = 1 if relevance > 0 else 0  # Assuming binary relevance
        dcg += gain / math.log2(i + 1)
    return dcg

# Function to calculate IDCG
def calculateIdcg(relevantDocs, k):
    # Chat GPT helped
    idcg = 0.0
    for i in range(min(k, len(relevantDocs))):
        idcg += sum([1 / math.log2(i + 2)]) # binary gain: 1 for relevant, 0 for non-relevant
    return idcg


def evaluateIRSystem(qrelPath, resultsPath):
    """
    Evaluate the information retrieval system based on qrels and result data.
    Handles the evaluation metrics for each query as per requirements.

    qrelPath: path to the qrel file
    resultsPath: path to the results file
    """
    try:
        # Parse the qrels and results files
        qrels = QrelsParser(qrelPath).parse()
        _, results = ResultsParser(resultsPath).parse()

        # Check if results are empty or incorrectly formatted (basic error handling)
        if not results.query_2_results:
            raise ValueError("Results data is empty or incorrectly formatted.")

        evaluationMetrics = {}

        # Loop over each query in the qrels
        for queryId in qrels.get_query_ids():
            retrievedDocs = results.get_result(queryId)  # Correct method to retrieve results
            if not retrievedDocs:
                continue  # If no docs retrieved for this query, skip to the next

            # retrievedDocsSorted = sorted(retrievedDocs, key=lambda x: (-x.score, x.doc_id))

            # Calling all the evaluation metrics 
            precisionAt10 = calculatePrecisionAtK(queryId, retrievedDocs, qrels, 10)
            ap = calculateAveragePrecision(queryId, retrievedDocs, qrels)
            dcgAt10 = calculateDcgAtK(queryId, retrievedDocs, qrels, 10)
            dcgAt1000 = calculateDcgAtK(queryId, retrievedDocs, qrels, 1000)

            relevant_docs = qrels.query_2_reldoc_nos[queryId]  # Correct way to access relevant docs
            idcgAt10 = calculateIdcg(relevant_docs, 10)
            idcgAt1000 = calculateIdcg(relevant_docs, 1000)
            
            ndcgAt10 = dcgAt10 / idcgAt10 if idcgAt10 > 0 else 0
            ndcgAt1000 = dcgAt1000 / idcgAt1000 if idcgAt1000 > 0 else 0

            evaluationMetrics[queryId] = {
                'precisionAt10': precisionAt10,
                'averagePrecision': ap,
                'ndcgAt10': ndcgAt10,
                'ndcgAt1000': ndcgAt1000
            }

        # Print the evaluation metrics for each query
        for queryId, metrics in evaluationMetrics.items():
            print(f"QueryID: {queryId}, P@10: {metrics['precisionAt10']:.4f}, ap: {metrics['averagePrecision']:.4f}, ndcg@10: {metrics['ndcgAt10']:.4f}, ndcg@1000: {metrics['ndcgAt1000']:.4f}")
        
        # Writing to a file in a table format to easily copy/paste it into excel
        # Chat GPT hlped with the formatting of this into a table
        with open('stem_evaluation_metrics.txt', 'w') as file:
            file.write(f"{'QueryID':<10} {'P@10':<10} {'AP':<10} {'NDCG@10':<10} {'NDCG@1000':<10}\n")
            for queryId, metrics in evaluationMetrics.items():
                file.write(f"{queryId:<10} {metrics['precisionAt10']:<10.4f} {metrics['averagePrecision']:<10.4f} {metrics['ndcgAt10']:<10.4f} {metrics['ndcgAt1000']:<10.4f}\n")


    except Exception as e:
        print(f"Error: Bad Format. Please fix the following error and try again: \n{str(e)}")
        sys.exit(1)



# Main method that uses command line arguments to accept file paths
if __name__ == '__main__':
    # Paths should be given as command line arguments or replaced with actual paths
    qrelPath = sys.argv[1] if len(sys.argv) > 1 else 'path/to/qrel/file'
    resultsPath = sys.argv[2] if len(sys.argv) > 2 else 'path/to/results/file'

    # Evaluate the IR system and output metrics
    evaluateIRSystem(qrelPath, resultsPath)
