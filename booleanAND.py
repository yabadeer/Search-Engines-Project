'''
Acknowledgements:
- Used Chat GPT to explain certain concepts such as using the sys and os packages.
- Used Stack Overflow, Geeks for Geeks, and Campuswire for help with syntax as well as some design influence.
- Will provide URLs for all links that are worth crediting and referencing.
- I have collaborated with Inesh Jacob and Vyomesh Iyengar on the logic of this program.
'''

import os
import sys

# Global Variables - mainly file names and exempt search topics.
LEXICON_FILE = "lexicon.txt"
INVERTED_INDEX_FILE = "inverted_index.txt"
MAPPING_FILE = "mapping.txt"
DOC_LENGTHS_FILE = "doc_lengths.txt"
EXCLUDED_TOPICS = {"416", "423", "437", "444", "447"}


def loadLexicon(indexPath):
    """
    Load the lexicon from the lexicon file.
    """
    lexicon = {}
    with open(os.path.join(indexPath, LEXICON_FILE), 'r') as f:
        for line in f:
            termID, term = line.strip().split(":")
            lexicon[int(termID)] = term
    return lexicon

def loadInvertedIndex(indexPath):
    """
    Load the inverted index from the file.
    This was a bit challenging due to the format of my inverted_index.txt file structure:
    termID: docID:count, docID:count, docID:count, ...
    """
    invertedIndex = {}
    with open(os.path.join(indexPath, INVERTED_INDEX_FILE), 'r') as f:
        for line in f:
            # Split only once on the first colon for termID.
            termID_str, postings_str = line.strip().split(":", 1)
            termID = int(termID_str)
            postingsList = []
            # Building the postings list for each termID.
            for posting in postings_str.split(","):
                docID, count = posting.split(":")
                postingsList.append((int(docID), int(count)))
            invertedIndex[termID] = postingsList
    return invertedIndex

def loadMapping(indexPath):
    """
    Load the mapping from docID to docno from the file.
    """
    mapping = {}
    with open(os.path.join(indexPath, MAPPING_FILE), 'r') as f:
        for line in f:
            docID, docno = line.strip().split(":")
            mapping[int(docID)] = docno
    return mapping


def tokenize(text):
    """
    Tokenizes the given text by downcasing all characters and treating sequences of alphanumerics as tokens.
    Using mainly the pseudocode from the lectures.
    This function is the same one as seen in the indexEngine.py program.
    """
    tokens = []
    text = text.lower()
    start = 0  # Starting index of a potential token

    for i in range(len(text)):
        if not text[i].isalnum():  # If the character is not alphanumeric
            if start != i:  # If there's a potential token between start and i
                token = text[start:i]
                tokens.append(token)
            start = i + 1  # Update the starting index for the next potential token

    # Handles the case where the last token extends to the end of the text
    if start < len(text):
        tokens.append(text[start:])

    return tokens

def booleanANDRetrieval(query, lexicon, invertedIndex):
    """
    Retrieve documents that contain all of the query's words using Boolean AND retrieval.
    Using logic described in class.
    """
    
    # Tokenizing each query.
    tokenizedQuery = tokenize(query)
    
    docSets = []
    # some minor help from chatGPT to debug the logic here
    for token in tokenizedQuery:
        termID = None
        for i, j in lexicon.items():
            # Checking if token is in the lexicon.
            if j == token:
                termID = i
                break
        if termID is not None:
            if termID in invertedIndex:
                docSets.append(set([doc[0] for doc in invertedIndex[termID]]))  # Extracting only docIDs.
    if not docSets:
        # If docSets is empty.
        return []
    resultSet = docSets[0]
    for docSet in docSets[1:]:
        # Calling intersection
        # Stack overflow: https://stackoverflow.com/questions/2541752/best-way-to-find-the-intersection-of-multiple-sets
        # W3Schools: https://www.w3schools.com/python/ref_set_intersection.asp
        resultSet = resultSet.intersection(docSet)
    return list(resultSet)

def extractQueriesFromTopics(inputFile, outputFile):
    """
    Extracts the topics' titles from the given file and saves them in the specified format.
    inputFile: The path to the topics.401-450.txt file.
    outputFile: The path to save the extracted queries.
    """
    with open(inputFile, 'r') as f:
        lines = f.readlines()

    with open(outputFile, 'w') as f:
        i = 0
        while i < len(lines):
            # Check if the line contains the string "Number:"
            if "Number:" in lines[i]:
                # Ensure the line contains a colon before attempting to split
                if ":" in lines[i]:
                    topicID = lines[i].split(":")[1].strip()
                    f.write(topicID + "\n")
                i += 1
                # Ensure the line contains the string "title" before attempting to extract the query
                if "<title>" in lines[i]:
                    query = lines[i].split("<title>")[1].split("</title>")[0].strip()
                    f.write(query + "\n")
            i += 1

def main():
    # Check command-line arguments.
    if len(sys.argv) != 4:
        print("Usage: python3 booleanAND <index_path> <queries_file> <output_file>")
        sys.exit(1)

    indexPath, queriesFile, outputFile = sys.argv[1], sys.argv[2], sys.argv[3]

    # Load lexicon and inverted index.
    lexicon = loadLexicon(indexPath)
    invertedIndex = loadInvertedIndex(indexPath)

    # Extract the queries.
    extractQueriesFromTopics("topics.1-5.txt", queriesFile)
    
    # Load the mapping.
    docIDToDOCNO = loadMapping(indexPath)

    # Process each query and write results to the output file.
    with open(queriesFile, 'r') as qf, open(outputFile, 'w') as outf:
        while True:
            topicID = qf.readline().strip()
            # Run until you run out of queries.
            if not topicID:
                break
            if topicID in EXCLUDED_TOPICS:
                qf.readline()  # Skip the query line for the excluded topic.
                continue  # Skip to the next iteration.
            query = qf.readline().strip()
            docIDs = booleanANDRetrieval(query, lexicon, invertedIndex)
            for rank, docID in enumerate(docIDs, 1):
                docno = docIDToDOCNO[docID]  # Convert docID to docno.
                score = len(docIDs) - rank
                # Output in the TREC format required.
                outf.write(f"{topicID} Q0 {docno} {rank} {score} yabadeerAND\n")

if __name__ == "__main__":
    main()
