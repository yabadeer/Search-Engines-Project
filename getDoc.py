'''
Acknowledgements:
- Used Chat GPT to explain certain concepts such as using the sys and os packages.
- Used Stack Overflow, Geeks for Geeks, and Campuswire, for help with syntax as well as some design influence.
- Will provide URLs for all links that are worth crediting and referencing.
'''

import os # to help with creating directories
import sys # to help catch errors with user input in the terminal

def fetchDocumentByDocNo(indexPath, docNo):
    """
    Fetches a document by its DOCNO from the storage.
    outputPath: The path where the documents are stored.
    docNo: The DOCNO of the desired document.
    """
    # Extracting the date from the DOCNO to build the directory path
    year, month, day = '19' + docNo[6:8], docNo[2:4], docNo[4:6]
    # Constructing the directory path based on the date
    directoryPath = os.path.join(indexPath, year, month, day)
    # Construct the file path by appending the DOCNO to the directory path
    filePath = os.path.join(directoryPath, docNo + '.txt')
    
    # Check if the file exists at the constructed path
    if not os.path.exists(filePath):
        return "This document doesn't exist. Please try searching again with a valid DOCNO."
    
    # If the file exists, open it and return its content
    with open(filePath, 'r') as f:
        return f.read()

def fetchDocumentByInternalId(indexPath, internalId):
    """
    Fetches a document by its internal ID.
    This function converts the internal ID to a DOCNO, then calls the function above to return the whole document.
    """
    # Open the mapping file that contains the relationship between internal IDs and DOCNO
    ## Reference: https://www.geeksforgeeks.org/python-os-path-join-method/
    with open(os.path.join(indexPath, "mapping.txt"), "r") as map_file:
        # Read all the lines (each line represents a mapping) and store it in a list
        ## Inspired from campuswire: https://campuswire.com/c/G6DF2065F/feed/23
        docNos = map_file.readlines()
        
        if internalId < len(docNos): # checking if it's a valids DOCNO we have
            # Split the line at the colon to get the correct DOCNO
            docNo = docNos[internalId-1].split(":")[1].strip()
            return fetchDocumentByDocNo(indexPath, docNo) # Fetch the document using the extracted DOCNO
    return "This document doesn't exist. Please try searching again with a valid ID."

def main():
    """
    Main function to fetch a document by its DOCNO or internal ID.
    """
    # Checking if the correct number of command line arguments are provided.
    if len(sys.argv) != 4:
        print("Error: Please provide all the required arguments: python3 getDoc.py <path_to_store> <mode: 'id' or 'docno'> <value>")
        sys.exit(1)

    # Extracting the provided arguments
    indexPath = sys.argv[1] 
    modeOfSearch = sys.argv[2] # DOCNO or id
    value = sys.argv[3]

    # Fetch the document based on the provided mode (either by DOCNO or internal ID)
    if modeOfSearch == "docno":
        print(fetchDocumentByDocNo(indexPath, value))
    elif modeOfSearch == "id":
        print(fetchDocumentByInternalId(indexPath, int(value)))
    else:
        print("Invalid mode. Please search a doc using the 'DOCNO' or 'id'.")

if __name__ == "__main__":
    main()