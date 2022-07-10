from math import sqrt, log2

def checkIndex(query, invertedIndex, phraseSearch = True):
    """
    Implementing early stop. Check if query words are in inverted index or not.
    :param query:
    :param invertedIndex:
    :return: True if words can be found, false otherwise.
    """
    if phraseSearch:
        for word in query:
            if word not in invertedIndex:
                print(word + " not a valid entry")
                return False
        return True
    else:
        for word in query:
            if word == "and" or word == "or" or word == "but":
                continue
            if word not in invertedIndex:
                return False
        return True

def rankBySecondElem(list):
    """
    Helper function to be used in cosineSimRanking.
    :param list: list of the form [[docid1, rankingScore1], [docod2, rankingScore2]...
    :return: Sorted list by second entry.
    """
    return list[1]


def cosineSimRanking(query, invertedIndex, docTable, relevantDocs):
    """
    Ranks preform cosine similarity ranking.
    :param query: User query must be preprocessed as a list of words
    :param relevantDocs: Hash table of document information
    :return: Sorted rank list with entries [docid, cosine similarity score].
    """
    rankedList = []

    for docID in relevantDocs:
        normalize = 1 / sqrt(docTable[docID]['doc vec len'])
        vecSum = 0
        for word in query:
            vecSum += invertedIndex[word]['doc id'][docID]['tf-idf']
        cosineScore = normalize * (1/len(query)) * vecSum
        rankedList.append([docID, cosineScore])
    return sorted(rankedList, key=rankBySecondElem, reverse=True)


def phrasalSearch(query, invertedIndex, docTable):
    """
    Preform phrasalSearch.
    :param query: Search query.
    :param invertedIndex: Inverted index
    :param docTable: Document table.
    :return: List of lists, by correlationg rank.
    """
    query = query[1:len(query) - 1].lower().strip().split()

    if checkIndex(query, invertedIndex):
        if len(query) == 1:
            print("send to boolean (will be or)")
            return booleanSearch(''.join(query), invertedIndex, docTable)
        else:
            # multiple words in phrasal search, first we find relevant documents (all words must have intersection)
            relevantDocs = set(invertedIndex[query[0]]['doc id'])
            for word in query:
                relevantDocs = relevantDocs & set(invertedIndex[word]['doc id'].keys())

            finalDocs = []
            for document in relevantDocs:
                for num in range(0, len(query) - 1):
                    startArr = invertedIndex[query[num]]['doc id'][document]['posting']
                    inNextArr = any(item in list(map(lambda x: x + 1, startArr)) \
                                    for item in invertedIndex[query[num + 1]]['doc id'][document]['posting'])
                    if not inNextArr:
                        break
                    finalDocs.append(document)

            return cosineSimRanking(query, invertedIndex, docTable, finalDocs), query
    else:
        return "Last entry not valid."

def booleanSearch(query, invertedIndex, docTable):
    if type(query) != type(list()):
        query = query.split()
    if checkIndex(query, invertedIndex, phraseSearch = False):
        if "and" in query:
            print("Conducting AND query...")
            # multiple words in phrasal search, first we find relevant documents (all words must have intersection)
            relevantDocs = set(invertedIndex[query[0]]['doc id'])
            for word in query:
                if word != "and":
                    relevantDocs = relevantDocs & set(invertedIndex[word]['doc id'].keys())

            finalRanking = {}

            for docID in relevantDocs:
                for word in query:
                    if word != "and":
                        if docID not in finalRanking:
                            finalRanking[docID] = docTable[docID]['extended table'][word]['tf-idf']
                        else:
                            finalRanking[docID] += docTable[docID]['extended table'][word]['tf-idf']
            try:
                query.remove("and")
            except:
                pass
            return list(map(list, sorted(list(finalRanking.items()), key=rankBySecondElem, reverse=True))), query
        elif "but" in query:
            relevantDocs = []
            removingDocs = []
            print("Conducting BUT query...")
            locationOfBut = query.index("but")
            leftSideOfQuery = query[:locationOfBut]
            rightideOfQuery = query[locationOfBut + 1:]

            # Get documents that must be included
            for word in leftSideOfQuery:
                relevantDocs.append(list(invertedIndex[word]['doc id'].keys()))

            # Flatten list
            relevantDocs = sum(list(relevantDocs),[])

            # Get documents that must be removed
            for word in rightideOfQuery:
                removingDocs.append(list(invertedIndex[word]['doc id'].keys()))
            # Flatten list
            removingDocs = sum(list(removingDocs), [])

            finalRelevantDocs = [doc for doc in relevantDocs if doc not in removingDocs]

            # Obtain correlation
            finalRanking = {}
            for docID in finalRelevantDocs:
                for word in leftSideOfQuery:
                    if word != "but":
                        if docID not in finalRanking:
                            finalRanking[docID] = docTable[docID]['extended table'][word]['tf-idf']
                        else:
                            finalRanking[docID] += docTable[docID]['extended table'][word]['tf-idf']
            try:
                query.remove("but")
            except:
                pass
            return list(map(list, sorted(list(finalRanking.items()), key=rankBySecondElem, reverse=True))), leftSideOfQuery
        else:
            print("Conducting OR query...")
            relevantDocs = []
            for word in query:
                if word != "or":
                    relevantDocs.append(list(invertedIndex[word]['doc id'].keys()))

            relevantDocs = list(set(sum(list(relevantDocs), [])))

            finalRanking = {}
            for docID in relevantDocs:

                for word in query:
                    if word != "or":
                        if docID not in finalRanking:
                            if word in docTable[docID]['extended table'].keys():
                                finalRanking[docID] = invertedIndex[word]['doc id'][docID]['tf-idf']
                        else:
                            if word in docTable[docID]['extended table'].keys():
                                finalRanking[docID] += invertedIndex[word]['doc id'][docID]['tf-idf']
            try:
                query.remove("or")
            except:
                pass
            return list(map(list, sorted(list(finalRanking.items()), key=rankBySecondElem, reverse=True))), query
