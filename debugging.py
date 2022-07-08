
def wordBasedCorrelation(invertedIndex, docTable):
    wordBasedCorrelationDic = {}

    for wordKey in invertedIndex.keys():
        print(wordBasedCorrelationDic)
        for wordEntry in invertedIndex.keys():
            if wordEntry not in wordBasedCorrelationDic.keys():
                wordBasedCorrelationDic[wordKey] = {
                    'df' : invertedIndex[wordKey]['df'],
                    'term': {wordEntry: {'correlation': 1}}
                }
            else:
                if wordEntry not in wordBasedCorrelationDic[wordEntry]['term'].keys():
                        try:
                            wordBasedCorrelationDic[wordKey]['term'][wordEntry] = 1
                        except:
                            pass

    # for item in wordBasedCorrelationDic.keys():
    #     print(item)
    #     print(wordBasedCorrelationDic[item])
