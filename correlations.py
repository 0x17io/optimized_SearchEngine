def rankBySecondElem(list):
    """
    Helper function to be used in cosineSimRanking.
    :param list: list of the form [[docid1, rankingScore1], [docod2, rankingScore2]...
    :return: Sorted list by second entry.
    """
    return list[1]

def wordBasedCorrelation(query, invertedIndex, docTable, rankedDocList):
    topRankedPagesA = [page[0] for page in rankedDocList][:2]

    extractedKeyWordsK = []

    for page in topRankedPagesA:
        extractedKeyWordsK.append(list(docTable[page]['extended table'].keys()))
    extractedKeyWordsK = list(set(sum(extractedKeyWordsK, [])))

    correlationWords = {}

    for docID in topRankedPagesA:
        for word in query:
            if word not in docTable[docID]['extended table'].keys():
                continue
            for keyword in extractedKeyWordsK:
                if keyword not in docTable[docID]['extended table'].keys():
                    continue
                word_tf_idf = invertedIndex[word]['doc id'][docID]['tf-idf']
                key_tf_idf = invertedIndex[keyword]['doc id'][docID]['tf-idf']
                if keyword not in correlationWords:
                    correlationWords[keyword] = word_tf_idf * key_tf_idf
                else:
                    correlationWords[keyword] += word_tf_idf * key_tf_idf
    top_words = list(map(list, sorted(list(correlationWords.items()), key=rankBySecondElem, reverse=True)))[:5]
    top_words = [word[0] for word in top_words]
    return top_words[:5]

def docBasedCorrelation(query, invertedIndex, docTable, rankedDocList):
    topPagesA = [page[0] for page in rankedDocList]
    print(topPagesA)
    documenCorrelation = {}
    for docID in topPagesA:
        topPagesAset = set(docTable[docID]['extended table'].keys())
        for docIDInDocTable in docTable.keys():
            genDoc = set(docTable[docIDInDocTable]['extended table'].keys())
            if docID not in documenCorrelation:
                #topPagesAset = set(docTable[])
                documenCorrelation[docID] = docTable[['extended table']]
            else:
                continue

        print(docID)
        print(docTable[docID])

