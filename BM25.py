'''
Acknowledgements:
- I relied on code / pseudocode provided by the prof. I utilized many import statements.
- Used Chat GPT to help me implement some features (will acknowledge when applicable).
- Will provide URLs for all links that are worth crediting and referencing.
- I collaborated with Inesh Jacob on some of the concepts of this assignment (bm25 logic).
'''

import math
import os
import sys
import time
import re
import heapq
from indexEngine import tokenize
from getDoc import fetchDocumentByDocNo
from collections import defaultdict

# Define global variables for the file names of the data structures.
LEXICON_FILE = "lexicon.txt"
INVERTED_INDEX_FILE = "inverted_index.txt"
MAPPING_FILE = "mapping.txt"
DOC_LENGTHS_FILE = "doc-lengths.txt"

# Dictionary to convert numerical months to full word strings
MONTHS = {
    '01': 'January',
    '02': 'February',
    '03': 'March',
    '04': 'April',
    '05': 'May',
    '06': 'June',
    '07': 'July',
    '08': 'August',
    '09': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December'
}

def loadLexicon(indexPath):
    """
    Load the lexicon from the lexicon file.
    Args:
        indexPath (str): The directory path where the lexicon file is located.
    Returns:
        dict: A dictionary mapping terms to their term IDs.
    """
    lexicon = {}
    # Open the lexicon file and read line by line.
    with open(os.path.join(indexPath, LEXICON_FILE), 'r') as f:
        for line in f:
            # Split each line into term ID and term.
            termID, term = line.strip().split(":")
            # Map the term to its term ID in the lexicon dictionary.
            lexicon[term] = int(termID)
    return lexicon

def loadInvertedIndex(indexPath):
    """
    Load the inverted index from a file.
    Returns:
        dict: A dictionary representing the inverted index.
    """
    invertedIndex = {}
    # Open the inverted index file and read line by line.
    with open(os.path.join(indexPath, INVERTED_INDEX_FILE), 'r') as f:
        for line in f:
            # Split the line into term ID and postings string.
            termID_str, postings_str = line.strip().split(":", 1)
            termID = int(termID_str)
            postingsList = []
            # Process each posting in the postings string.
            for posting in postings_str.split(","):
                # Split the posting into document ID and count.
                docID, count = posting.split(":")
                # Add the document ID and count to the postings list.
                postingsList.append((int(docID), int(count)))
            # Add the postings list to the inverted index, keyed by the term ID.
            invertedIndex[termID] = postingsList
    return invertedIndex

def loadMapping(indexPath):
    """
    Load the mapping of document IDs to DOCNOs.
    Returns:
        dict: A dictionary mapping document IDs to DOCNOs.
    """
    mapping = {}
    # Open the mapping file and read line by line.
    with open(os.path.join(indexPath, MAPPING_FILE), 'r') as f:
        for line in f:
            # Split the line into document ID and DOCNO.
            docID_str, docno = line.strip().split(":")
            # Map the document ID to the DOCNO in the mapping dictionary.
            mapping[int(docID_str)] = docno
    return mapping

def loadDocLengths(indexPath):
    """
    Load the document lengths from a file.
    Returns:
        dict: A dictionary mapping document IDs to their lengths.
    """
    docLengths = {}
    # Open the document lengths file and read line by line.
    with open(os.path.join(indexPath, DOC_LENGTHS_FILE), "r") as file:
        for line in file:
            # Split the line into document ID and length.
            docId, length = line.strip().split(":")
            # Map the document ID to its length in the docLengths dictionary.
            docLengths[int(docId)] = int(length)
    return docLengths

def bm25Score(docId, queryTerms, k1, b, docLengths, avgDl, N, lexicon, invertedIndex):
    """
    Calculate the BM25 score for a document given a query.
    
    Args:
        docId (int): The ID of the document for which to calculate the score.
        queryTerms (list): The list of query terms.
        k1 (float): The BM25 parameter k1.
        b (float): The BM25 parameter b.
        docLengths (dict): A dictionary of document lengths.
        avgDl (float): The average document length.
        N (int): The total number of documents.
        lexicon (dict): A dictionary mapping terms to term IDs.
        invertedIndex (dict): The inverted index.
   
    Returns:
        float: The BM25 score for the document.
    """
    score = 0.0
    # Get the length of the document.
    dl = docLengths.get(docId, 0)
    # Calculate the score for each term in the query.
    for term in queryTerms:
        # Get the term ID from the lexicon.
        termId = lexicon.get(term)
        if termId is not None:
            # Get the postings list for the term ID from the inverted index.
            postingsList = invertedIndex.get(termId, [])
            # Find the count of the term in the document.
            f_i = next((count for docID, count in postingsList if docID == docId), 0)
            # Calculate the number of documents containing the term.
            n_i = len(postingsList)/2
            # Calculate the inverse document frequency.
            idf = math.log((N - n_i + 0.5) / (n_i + 0.5))
            # Calculate the BM25 term frequency component.
            k = k1 * ((1 - b) + b * (dl / avgDl))
            # Calculate the term's contribution to the total score.
            termScore = idf * f_i / (f_i + k)
            score += termScore
    return score

def bm25(query, lexicon, invertedIndex, docLengths, avgDl, N, k1, b):
    """
    Calculate BM25 scores for all documents in the corpus with respect to the given query.

    Args:
        query (str): The search query.
        lexicon (dict): Mapping of terms to term IDs.
        invertedIndex (dict): Mapping of term IDs to postings lists.
        docLengths (dict): Mapping of document IDs to document lengths.
        avgDl (float): Average document length in the corpus.
        N (int): Total number of documents in the corpus.
        k1 (float): BM25 tuning parameter for term frequency saturation.
        b (float): BM25 tuning parameter for document length normalization.

    Returns:
        list: Sorted list of tuples (docID, score) with the highest scoring documents first.
    """
    # Tokenize the query into individual terms.
    queryTerms = tokenize(query)

    # Initialize a dictionary to hold document scores.
    scores = defaultdict(float)

    # Iterate through each term in the query.
    for term in queryTerms:
        # Retrieve the term ID from the lexicon.
        termId = lexicon.get(term)
        # Check if the term exists in the corpus.
        if termId is not None:
            # Retrieve the postings list for the term from the inverted index.
            postingsList = invertedIndex.get(termId, [])
            # Calculate scores for each document in the postings list.
            for docId, _ in postingsList:
                # Get the BM25 score for the document with respect to the term.
                score = bm25Score(docId, queryTerms, k1, b, docLengths, avgDl, N, lexicon, invertedIndex)
                # Accumulate scores for each document across all terms in the query.
                scores[docId] += score

    # Sort the documents by their accumulated scores in descending order.
    sortedScores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return sortedScores

def extractHeadlineAndDate(documentContent, docNo, snippet):
    # Initialize default values
    headline = "(Headline not found)"
    year, month, day = '19' + docNo[6:8], docNo[2:4], docNo[4:6]

    if '<HEADLINE>' in documentContent and '</HEADLINE>' in documentContent:
        # Extract headline
        headlineContent = documentContent.split('<HEADLINE>')[1].split('</HEADLINE>')[0].strip()
        headline = headlineContent.replace('<P>', '').replace('</P>', '').replace('\n', '').strip()
    elif snippet:
        # Use the first 50 characters of the snippet as headline if the headline is not found
        headline = snippet[:50] + "..." if len(snippet) > 50 else snippet

    return headline, year, month, day

def displayTopResults(scores, mapping, indexPath, query, topN):
    for rank, (docId, score) in enumerate(scores[:topN], 1):
        docNo = mapping.get(docId, "UnknownDOCNO")
        documentContent = fetchDocumentByDocNo(indexPath, docNo)
        snippet = generateQueryBiasedSnippet(documentContent, tokenize(query))
        headline, year, month, day = extractHeadlineAndDate(documentContent, docNo, snippet)
        print(f"{rank}. {headline} ({MONTHS[month]} {day}, {year})\n{snippet} ({docNo})\n")

def stripTags(text):
    # Removing tags
    # Reference: https://stackoverflow.com/questions/3662142/how-to-remove-tags-from-a-string-in-python-using-regular-expressions-not-in-ht
    return re.sub(r'<[^>]+>', '', text)

def getTextContent(documentContent):
    # Extracting text between <TEXT> tags
    textContent = ""
    if '<TEXT>' in documentContent and '</TEXT>' in documentContent:
        textContent = documentContent.split('<TEXT>')[1].split('</TEXT>')[0]
    return textContent

def splitIntoSentences(text):
    # Splitting sentences
    # Reference: https://stackoverflow.com/questions/44099714/how-to-use-re-split-for-commas-and-periods
    sentences = re.split(r'[.!?]', text)
    return [sentence.strip() for sentence in sentences if sentence]

def processDocumentForSnippets(documentContent):
    textContent = getTextContent(documentContent)
    cleanText = stripTags(textContent)
    sentences = splitIntoSentences(cleanText)
    # Filtering out sentences less than 5 words
    return [(sentence, tokenize(sentence)) for sentence in sentences if len(sentence.split()) >= 5]

def calculateSentenceMetrics(sentence, queryTerms):
    # From pseudo-code provided by Professor Smucker in lecture
    c = sum(word in queryTerms for word in sentence)
    d = len(set(sentence) & set(queryTerms))
    k = findLongestRun(queryTerms, sentence)
    return c, d, k

def findLongestRun(queryTerms, sentence):
    # ChatGPT assisted with some logic errors I previously had
    max_run = 0
    current_run = 0
    for word in sentence:
        if word in queryTerms:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 0
    return max_run

def cleanAndJoinSentences(sentences):
    # Join sentences and ensure the last sentence ends with a period for formatting purposes
    combined = '. '.join(sentences).strip()
    if not combined.endswith('.'):
        combined += '.'
    return combined

# Generating the snippets / summaries
def generateQueryBiasedSnippet(documentContent, queryTerms):
    sentences = processDocumentForSnippets(documentContent)
    maxHeap = []
    for index, (sentence, tokenizedSentence) in enumerate(sentences):
        # calculating h
        if index == 0:
            h = 1
        else:
            h = 0

        # Calculating l
        if index == 1:
            l = 2
        elif index == 2:
            l = 1
        else:
            l = 0
        
        c, d, k = calculateSentenceMetrics(tokenizedSentence, queryTerms)
        score = c + d + k + h + l
        heapq.heappush(maxHeap, (-score, sentence))

    # Forming the summary
    summary = []
    # 2 sentence Query Biased Summary
    while maxHeap and len(summary) < 2:
        # ChatGPT assisted with max heap logic
        _, sentence = heapq.heappop(maxHeap)
        summary.append(sentence.replace('\n', ' '))  # Replace newlines with spaces (for formatting)

    # Cleaning and joining sentences
    finalSnippet = cleanAndJoinSentences(summary)
    return finalSnippet

def main():
    indexPath = sys.argv[1]
    # Load necessary data structures
    lexicon = loadLexicon(indexPath)
    invertedIndex = loadInvertedIndex(indexPath)
    docLengths = loadDocLengths(indexPath)
    mapping = loadMapping(indexPath)
    avgDl = sum(docLengths.values()) / len(docLengths)
    N = len(docLengths)

    while True:
        # User input
        query = input("Enter your query (or type 'Q' to quit): ")
        if query.lower() == 'q': # Quitting condition
            break

        # Timing the retrieval. ChatGPT informed me of the library to use
        start_time = time.time()
        scores = bm25(query, lexicon, invertedIndex, docLengths, avgDl, N, k1=1.2, b=0.75)
        retrieval_time = time.time() - start_time

        # Printing out the top N (N = 10) results to the terminal
        displayTopResults(scores, mapping, indexPath, query, 10)

        print(f"Retrieval took {retrieval_time:.2f} seconds.")

        while True:
            # New query or quit
            choice = input("Enter a rank to view the document, 'N' for a new query, or 'Q' to quit: ")
            if choice.lower() == 'n':
                break
            elif choice.lower() == 'q':
                return
            # View specific rank
            elif choice.isdigit():
                rank = int(choice)
                if 1 <= rank <= len(scores):
                    docId = scores[rank - 1][0]
                    docNo = mapping[docId]
                    document_content = fetchDocumentByDocNo(indexPath, docNo)
                    print(document_content)
                else:
                    print("Invalid rank number. Please try again.")
            else:
                print("Invalid input. Please try again.")

if __name__ == "__main__":
    main()
