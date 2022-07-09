import numpy as np

def wordBasedCorrelation(invertedIndex, docTable):
    wordBasedCorrelationDic = {}

    #print(invertedIndex)
    for keyWord in invertedIndex.keys():
        keyWordDocSet = invertedIndex[keyWord]['doc id']
        for wordEntry in invertedIndex.keys():
            wordEntryDocSet = invertedIndex[wordEntry]['doc id']

            inner_product = sum({docID:keyWordDocSet[docID].get('tf-idf',0)*wordEntryDocSet[docID].get('tf-idf',0) \
                   for docID in set(keyWordDocSet.keys() & wordEntryDocSet.keys()) }.values())
            if inner_product != 0:
                if keyWord not in wordBasedCorrelationDic:
                    wordBasedCorrelationDic[keyWord] = [[wordEntry, inner_product]]
                else:
                    wordBasedCorrelationDic[keyWord].append([wordEntry, inner_product])

        # print(wordBasedCorrelationDic)
    #print(wordBasedCorrelationDic)
    return wordBasedCorrelationDic
    # for item, value in wordBasedCorrelationDic.items():
    #     print(str(item), sorted(value, key = lambda x: x[1], reverse=True))

def docBasedCorrelation(docTable):
    # topPagesA = [page[0] for page in rankedDocList]
    # print(topPagesA)
    documenCorrelation = {}
    for docID in docTable.keys():
        docIDName = docID
        docID = docTable[docID]['extended table']

        for docIDEntry in docTable.keys():
            docIDEntryName = docIDEntry
            docIDEntry = docTable[docIDEntry]['extended table']
            inner_product = sum({word: docID[word].get('tf-idf', 0) * docIDEntry[word].get('tf-idf', 0) \
                                 for word in (set(docID.keys()) & set(docIDEntry.keys()))}.values())
            # docID[word].get('tf-idf', 0) * docIDEntry[word].get('tf-idf', 0)
            if inner_product != 0:
                if docIDName not in documenCorrelation:
                    documenCorrelation[docIDName] = [[docIDEntryName, inner_product]]
                else:
                    documenCorrelation[docIDName].append([docIDEntryName, inner_product])
            # if docID not in documenCorrelation:
            #     #topPagesAset = set(docTable[])
            #     documenCorrelation[docID] = docTable[['extended table']]
            # else:
            #     continue
    for item, value in documenCorrelation.items():
        print(str(item), sorted(value, key = lambda x: x[1], reverse=True))
    # print(docID)
    # print(docTable[docID])
    print("---proof")
    for item, value in docTable.items():
        print(str(item), value['extended table'])
