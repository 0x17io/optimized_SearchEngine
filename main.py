##################################################################################################
# Created By: Srikanth Akiti, Sonya Cirlos, Jose Ruben Espinoza, Marlon Martinez, Albert Trevino #
# Project Title: Web Search Project                                                              #
# Date Range: Summer I 2022                                                                      #
# Short Description: Web search engine implementation using an inverted index tables.            #
##################################################################################################

from zipfile import ZipFile
from bs4 import BeautifulSoup
from math import sqrt, log2
from collections import deque
from datetime import datetime
from query_operations import searchFunctions
from correlation_optimizations import correlations
archive = ZipFile('cheDoc.zip', 'r')

# Top 100 most frequently used words (excluding or, and, but). source wiki
stop_words = ['the', 'be', 'to', 'of', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he',
              'as', 'you', 'do', 'at', 'this', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
              'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about',
              'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
              'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than',
              'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two',
              'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give',
              'day', 'most', 'us']
inverted_index = {}
document_table = {}

queueFIFO = deque()
visitedURLs = set()


def buildIndexTables(root='rhf/index.html'):

    # Load starting file.
    #queueFIFO.append(root)
    queueFIFO.extend(archive.namelist())

    while queueFIFO:

        url_link = queueFIFO.popleft()

        if url_link in visitedURLs:
            continue

        document_table[url_link] = {
            'doc vec len': 0,
            'max freq': 1,
            'extended table': {}
        }

        # Error handling, some files have unknown types. Idea was taken from Dr. Chen's HW assistance.
        try:
            # Note that the following URLS are not valid, but being produced by the algorithm:
            # rhf/www.netfunny.com/rhf/jokes/93q3/external.html
            # rhf/www.netfunny.com/rhf/jokes/93q3//rhf/best.html
            # rhf/www.netfunny.com/rhf/jokes/96/Apr/-.html
            file_contents = archive.read(url_link)
        except:
            continue
        try:
            file_contents.decode('utf-8', errors='ignore')
        except:
            try:
                file_contents.decode()
            except:
                continue

        soup = BeautifulSoup(file_contents, 'html.parser')

        current_file_text = soup.get_text().lower().split()

        current_file_text = [word for word in current_file_text \
                             if word.isalpha() and word not in stop_words]

        # Update inverted Index
        for index, word in enumerate(current_file_text):
            if word not in inverted_index.keys():
                inverted_index[word] = {
                    'df': 0,
                    'doc id': {url_link : {'freq': 1, 'tf-idf': 0, 'posting': [index]}}
                }
            else:
                if url_link not in inverted_index[word]['doc id']:
                    inverted_index[word]['doc id'][url_link]= {'freq': 1, 'tf-idf': 0, 'posting': [index]}
                else:
                    inverted_index[word]['doc id'][url_link]['posting'].append(index)
            inverted_index[word]['df'] = len(inverted_index[word]['doc id'])
            inverted_index[word]['doc id'][url_link]['freq'] = len(inverted_index[word]['doc id'][url_link]['posting'])

            if inverted_index[word]['doc id'][url_link]['freq'] > document_table[url_link]['max freq']:
                document_table[url_link]['max freq'] = inverted_index[word]['doc id'][url_link]['freq']

        # Obtain all unique URLS from currently held document.
        allLinks = set([links.get('href') for links in soup.find_all('a', href=True) \
                        if ".." not in links.get('href') and "#" not in links.get('href') \
                        and "/" not in links.get('href')[-1] and \
                        (".html" in links.get('href') or ".htm" in links.get('href'))])
        for url in allLinks:
            path = '/'.join(url_link.split("/")[:-1]) + "/"
            queueFIFO.append(path + url)

        # Add newly found urls to queue.
        visitedURLs.add(url_link)

    #print(document_table.values())

    for word, values in inverted_index.items():
        df_value = inverted_index[word]['df']
        for docID in values['doc id'].keys():
            freq = inverted_index[word]['doc id'][docID]['freq']
            max_freq = document_table[docID]['max freq']
            normalization = log2(len(document_table) / (df_value + 1)) + 1

            final_tf_idf = freq / max_freq * normalization
            inverted_index[word]['doc id'][docID]['tf-idf'] = final_tf_idf
            document_table[docID]['extended table'].update({word : {'tf-idf' : final_tf_idf}})

            document_table[docID]['doc vec len'] += final_tf_idf * final_tf_idf


def webSearch(invertedIndex, docTable):
    """
    Web engine console.
    :param invertedIndex: Inverted index table.
    :param docTable: Table containing doc information
    :return:
    """
    print("Now the search beings:")
    searchEntry = input("enter a search key=>")
    while (searchEntry != ""):
        # Check for phrasal first.
        if "\"" in searchEntry:
            print("Preforming phrasal search...")
            top_docs, query = searchFunctions.phrasalSearch(searchEntry, invertedIndex, docTable)

            # Refine Query based on top 5 keywords
            redefinedQuery = correlations.wordBasedCorrelation(query,invertedIndex,docTable,top_docs)
            top_docs, query = searchFunctions.booleanSearch(redefinedQuery, invertedIndex, docTable)

            # Refine recommendation based on 5 top pages
            top_docs = correlations.docBasedCorrelation(query, invertedIndex, docTable, top_docs)
            print(top_docs)
        elif len(searchEntry.split()) == 1:
            print("Only searching for one word...")
            top_docs, query = searchFunctions.booleanSearch(searchEntry, invertedIndex, docTable)

            # Refine Query based on top 5 keywords
            redefinedQuery = correlations.wordBasedCorrelation(query, invertedIndex, docTable, top_docs)
            top_docs, query = searchFunctions.booleanSearch(redefinedQuery, invertedIndex, docTable)

            # Refine recommendation based on 5 top pages
            top_docs = correlations.docBasedCorrelation(query, invertedIndex, docTable, top_docs)
            print(top_docs)

        else:
            print("Preforming boolean search...")
            top_docs, query = searchFunctions.booleanSearch(searchEntry, invertedIndex, docTable)
            # Refine Query based on top 5 keywords
            redefinedQuery = correlations.wordBasedCorrelation(query, invertedIndex, docTable, top_docs)
            top_docs, query = searchFunctions.booleanSearch(redefinedQuery, invertedIndex, docTable)

            # Refine recommendation based on 5 top pages
            top_docs = correlations.docBasedCorrelation(query, invertedIndex, docTable, top_docs)
            print(top_docs)
        searchEntry = input("enter a search key=>")
    print("Bye")




if __name__ == '__main__':
    # a
    start_time = datetime.now()
    buildIndexTables()
    end_time = datetime.now()


    # for key, value in document_table.items():
    #     print(key)
    #     print(value)
    print(document_table['cheDoc/d1.html']['extended table'])
    print(document_table['cheDoc/d2.html']['extended table'])
    firstEntry = document_table['cheDoc/d1.html']['extended table']
    secondEntry = document_table['cheDoc/d2.html']['extended table']
    part1 = set(document_table['cheDoc/d1.html']['extended table'].keys())
    part2 = set(document_table['cheDoc/d2.html']['extended table'].keys())


    print(set(document_table['cheDoc/d1.html']['extended table'].keys()))
    print(set(document_table['cheDoc/d2.html']['extended table'].keys()))

    combiend = part1 & part2



    #webSearch(inverted_index,document_table)


