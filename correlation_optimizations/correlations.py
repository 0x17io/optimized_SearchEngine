# Similar to stop words in main, but added the 'and' 'or', 'but' entries
stop_words = ['the', 'be', 'to', 'of', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he',
              'as', 'you', 'do', 'at', 'this', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
              'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about',
              'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
              'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than',
              'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two',
              'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give',
              'day', 'most', 'us', 'and', 'or', 'but']

def wordBasedCorrelation(invertedIndex, query, topRanked, docTable):
    """
    Preform word correlations from words extracted from top ranked pages.
    :param invertedIndex: word inverted index dictionary.
    :param query: Initial query
    :param topRanked: Top ranked documents extracted after search.
    :param docTable:
    :return:
    """
    wordBasedCorrelationDic = {}
    topRankedA = topRanked[:5] # top 5 ranked pages
    kList = []
    for document in topRankedA:
        kList.append(list(docTable[document[0]]['extended table'].keys()))
    kListAsSet = set(sum(kList,[]))
    for keyWord in query:
        keyWordDocSet = invertedIndex[keyWord]['doc id']
        for wordEntry in kListAsSet:
            wordEntryDocSet = invertedIndex[wordEntry]['doc id']

            # Correlation value is based on inner dot product.
            inner_product = sum({docID:keyWordDocSet[docID].get('tf-idf',0)*wordEntryDocSet[docID].get('tf-idf',0) \
                   for docID in set(keyWordDocSet.keys() & wordEntryDocSet.keys()) }.values())
            if inner_product != 0:
                if keyWord not in wordBasedCorrelationDic:
                    wordBasedCorrelationDic[keyWord] = [[wordEntry, inner_product]]
                else:
                    wordBasedCorrelationDic[keyWord].append([wordEntry, inner_product])

    correlatedWords = []
    for key in wordBasedCorrelationDic:
        correlatedWords.append(wordBasedCorrelationDic[key])
    correlatedWords = sum(correlatedWords,[])
    correlatedWords = sorted(correlatedWords, key = lambda x: x[1], reverse=True)
    correlatedWords = [word[0] for word in correlatedWords if word[0] not in stop_words and word[0] not in query][:10]

    return correlatedWords

def docBasedCorrelation(docTable, top_docs):
    """
    Idea is the same as wordBasedCorrelation, except we utilize documents instead. Note there is room for optimization
    for this function.
    :param docTable: document table that was created during index building.
    :param top_docs: Top documents after word correlation is used.
    :return: Top correlated docs based on document correlation
    """
    documenCorrelation = {}
    for docID in top_docs[:5]:
        docIDName = docID[0]
        docID = docTable[docID[0]]['extended table']

        for docIDEntry in docTable.keys():
            docIDEntryName = docIDEntry
            docIDEntry = docTable[docIDEntry]['extended table']

            # Preform inner dot product.
            inner_product = sum({word: docID[word].get('tf-idf', 0) * docIDEntry[word].get('tf-idf', 0) \
                                 for word in (set(docID.keys()) & set(docIDEntry.keys()))}.values())

            if inner_product != 0:
                if docIDName not in documenCorrelation:
                    documenCorrelation[docIDName] = [[docIDEntryName, inner_product]]
                else:
                    documenCorrelation[docIDName].append([docIDEntryName, inner_product])
    correlatedDocs = []

    for key in documenCorrelation:
        correlatedDocs.append(documenCorrelation[key])

    correlatedDocs = sum(correlatedDocs,[])
    correlatedDocs = sorted(correlatedDocs, key = lambda x: x[1], reverse=True)

    return correlatedDocs

