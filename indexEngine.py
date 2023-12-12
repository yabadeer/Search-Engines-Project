'''
Acknowledgements:
- Used Chat GPT to explain certain concepts such as using the sys and os packages.
- Used Stack Overflow, Geeks for Geeks, and Campuswire for help with syntax as well as some design influence.
- Will provide URLs for all links that are worth crediting and referencing.
- I have collaborated with Inesh Jacob on the logic of this program.
'''

import os # to help with creating directories
import sys # to help catch errors with user input in the terminal
import gzip

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

# New or modified global variables
lexicon = {}  # Maps terms to their unique integer IDs
termStringToID = {}  # Maps integer IDs back to their corresponding terms
invertedIndex = {}  # The actual inverted index
docLengths = {}  # DOCNO to document length

def tokenize(text):
    """
    Tokenizes the given text by downcasing all characters and treating sequences of alphanumerics as tokens.
    Using mainly the pseudocode from the lectures.
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

def convertTokensToIDs(tokens):
    """
    Convert tokens to their corresponding integer IDs using the termStringToID.
    Building the lexicon: termID -> termString.
    Building the termStringToID: termString -> termID.
    Mainly using the pseudocode from the lecture.
    """
    tokenIDs = []
    for token in tokens:
        if token in termStringToID:
            tokenIDs.append(termStringToID[token])
        else:
            ID = len(termStringToID)
            termStringToID[token] = ID
            lexicon[ID] = token  # Populate lexicon dictionary here.
            tokenIDs.append(ID)
    return tokenIDs

def countWords(tokenIDs):
    """
    Count the occurrences of each token ID.
    Mainly using the pseudocode from class.
    """
    wordCounts = {}
    for ID in tokenIDs:
        if ID in wordCounts:
            wordCounts[ID] += 1
        else:
            wordCounts[ID] = 1
    return wordCounts

def addToPostings(wordCounts, docID):
    """
    Add the word counts of a document to the inverted index.
    Building the inverted index using individual posting lists.
    Mainly using the pseudocode from the lecture.
    """
    for termID in wordCounts:
        count = wordCounts[termID]
        if termID not in invertedIndex:
            invertedIndex[termID] = []
        invertedIndex[termID].append((docID, count))


def extractMetadataAndStoreDocument(documentContent, outputPath, internalId):
    """
    Extracts metadata, tokenizes content, updates lexicon and inverted index, and stores the documents and their metadata.
    """
    # Extract DOCNO
    docno = documentContent.split("<DOCNO>")[1].split("</DOCNO>")[0].strip()
    
    # Extracting the date from DOCNO
    year, month, day = '19' + docno[6:8], docno[2:4], docno[4:6]
    
    # Extract headline
    headline = "(Headline not found)" # initializing headline in the case it doesn't exist
    if '<HEADLINE>' in documentContent and '</HEADLINE>' in documentContent:
        # Extract everthing between the opening and closing tags
        headlineContent = documentContent.split('<HEADLINE>')[1].split('</HEADLINE>')[0].strip()
        # Removing the all other tags within the headline and removing new lines
        headline = headlineContent.replace('<P>', '').replace('</P>', '').replace('\n', '').strip()

    # Create directory structure based on date using the format yyyy / mm / dd / docs
    directoryPath = os.path.join(outputPath, year, month, day)
    os.makedirs(directoryPath, exist_ok=True)

    # Store the document in a .txt file
    with open(os.path.join(directoryPath, docno + '.txt'), 'w') as f:
        f.write(f"docno: {docno}\ninternal id: {internalId}\ndate: {MONTHS[month]} {day}, {year}\nheadline: {headline}\nraw document:\n{documentContent}")
    
    # Writing the mapping to the mapping.txt file
    with open(os.path.join(outputPath, "mapping.txt"), "a") as map_file:
        map_file.write(f"{internalId}:{docno}\n")
    
    # Tokenizing the content
    # Extract content from <HEADLINE> tag
    headlineContent = documentContent.split("<HEADLINE>")[1].split("</HEADLINE>")[0] if "<HEADLINE>" in documentContent else ""
    # Extract content from <TEXT> tag
    textContent = documentContent.split("<TEXT>")[1].split("</TEXT>")[0] if "<TEXT>" in documentContent else ""
    # Extract content from <GRAPHIC> tag
    graphicContent = documentContent.split("<GRAPHIC>")[1].split("</GRAPHIC>")[0] if "<GRAPHIC>" in documentContent else ""

    # Combine all the extracted contents
    content = " ".join([headlineContent, textContent, graphicContent])
    # Removing inner tags from all the text
    content_cleaned = removeTags(content)
    
    tokens = tokenize(content_cleaned) # Tokenize the contnet
    # Convert tokens to their integer IDs
    tokenIDs = convertTokensToIDs(tokens)
    # Count the occurrences of each token ID
    wordCounts = countWords(tokenIDs)
    # Add the word counts to the inverted index
    addToPostings(wordCounts, internalId)

    # After tokenizing the document
    docLength = len(tokens)
    docLengths[internalId] = docLength

    # Adding one to our internal integer ID count
    internalId += 1

    return internalId

def removeTags(content):
    '''
    Function to remove all inner tags within the <HEADLINE>, <TEXT>, and <GRAPHIC> tags.
    Used ChatGPT for inspiration behind the logic of this function.
    '''
    result = []
    inside_tag = False
    for char in content:
        if char == '<':
            inside_tag = True
        elif char == '>':
            inside_tag = False
        elif not inside_tag:
            result.append(char)
    return ''.join(result)

def main():
    """
    Main function to index and store documents and their metadata.
    """
    # Checking if the correct number of command line arguments are provided.
    ## Used Chat GPT here to explain to me what sys.argv does as I wasn't familiar with the package at the start of this assignment.
    if len(sys.argv) != 3:
        print("Error: Please provide all the required arguments to run properly: python3 indexEngine.py <path_to_latimes.gz> <path_to_store>")
        sys.exit(1)

    # Extracting the input file path and the output directory path from the command line arguments.
    inputPath = sys.argv[1]
    outputPath = sys.argv[2]

    # Checking if the input directory exists. If it does not, exit with an error message.
    if not os.path.exists(inputPath):
        print("Error: The specified input directory does not exist. Please choose an existing one and try again.")
        sys.exit(1)

    # Checking if the output directory already exists. If it does, exit with an error message.
    if os.path.exists(outputPath):
        print("Error: The specified directory already exists. Please choose something different and try again.")
        sys.exit(1)

    # Create the output directory.
    ## Reference: https://www.geeksforgeeks.org/python-os-makedirs-method/
    os.makedirs(outputPath)

    # Initializing the internal ID counter for the documents.
    internalId = 1
    # Initializing an empty string to accumulate the content of a document.
    documentContent = ""
    # Boolean to indicate if we are currently inside a <DOC>...</DOC> block.
    insideDoc = False

    # Opening the input file in read mode.
    ## Reference: https://stackoverflow.com/questions/10566558/read-lines-from-compressed-text-files
    with gzip.open(inputPath, 'rt') as f:
        # Processing the file line by line.
        for line in f:
            # Checking if the current line marks the start of a document.
            if "<DOC>" in line:
                insideDoc = True
            # If we are inside a document, add the content to our documentContent variable.
            if insideDoc:
                documentContent += line
            # Checking if the current line marks the end of a document.
            if "</DOC>" in line:
                insideDoc = False
                # Extract metadata from the accumulated document content and store the document.
                internalId = extractMetadataAndStoreDocument(documentContent, outputPath, internalId)
                # Reset the document content accumulator for the next document.
                documentContent = ""

    # Writing all required files to the latimes-index folder.
    # Lexicon: termID -> termString.
    with open(os.path.join(outputPath, "lexicon.txt"), "w") as f:
        for termID, term in lexicon.items():
            f.write(f"{termID}:{term}\n")
    
    # Reverse lexicon -> termStringToID: termString -> termID.
    with open(os.path.join(outputPath, "termStringToID.txt"), "w") as f:
        for term, termID in termStringToID.items():
            f.write(f"{term}:{termID}\n")

    # Inverted index -> termID: docID:count, docID:count, docID:count, ...
    with open(os.path.join(outputPath, "inverted_index.txt"), "w") as f:
        for termID, postings in invertedIndex.items():
            postingsStr = ', '.join([f"{docID}:{count}" for docID, count in postings])
            f.write(f"{termID}: {postingsStr}\n")

    # Doc lengths to specify how many tokens each document has.
    with open(os.path.join(outputPath, "doc-lengths.txt"), "w") as f:
        for docID, length in docLengths.items():
            f.write(f"{docID}: {length}\n")

# Entry point of the script.
if __name__ == "__main__":
    main()
 
