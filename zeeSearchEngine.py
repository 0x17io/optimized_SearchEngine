##################################################################################################
# Created By: Srikanth Akiti, Sonya Cirlos, Jose Ruben Espinoza, Marlon Martinez, Albert Trevino #
# Project Title: Web Search Project                                                              #
# Date Range: Summer I 2022                                                                      #
# Short Description: Web search engine implementation using an inverted index tables.            #
##################################################################################################
import numpy as np
from zipfile import ZipFile
from bs4 import BeautifulSoup
from math import log2
from collections import deque

from query_operations import searchFunctions
from correlation_optimizations import correlations
from flask import Flask, render_template, request
archive = ZipFile('rhf.zip', 'r')

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
    queueFIFO.append(root)
    #queueFIFO.extend(archive.namelist())

    while queueFIFO:

        url_link = queueFIFO.popleft()

        if url_link in visitedURLs:
            continue

        document_table[url_link] = {
            'doc vec len': 0,
            'max freq': 1,
            'extended table': {},
            'short description': ""
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

        try:
            document_table[url_link]['short description'] = soup.find("title").get_text()
        except:
            document_table[url_link]['title'] = "Title not available."

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

    # Work on updating tf-idf values
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

def rankBySecondElem(list):
    """
    Helper function to be used for sorting.
    :param list: list of the form [[docid1, rankingScore1], [docod2, rankingScore2]...
    :return: Sorted list by second entry.
    """
    return list[1]

def checkIndexFrontPage(query, invertedIndex):
    """
    Similear to checkIndexFrontPage found under SearchFunctions.py
    Checks if query has valid words from inverted index. Note, this code will only run if
    top docs are not available.
    :param query:
    :param invertedIndex:
    :return: True if words can be found, false otherwise.
    """

    if "\"" in query:
        query = query[1:len(query) - 1].lower().strip().split()
        for word in query:
            if word not in invertedIndex:
                print(word + " not a valid entry")
                return word
    else:
        query = query.split()
        for word in query:
            if word == "and" or word == "or" or word == "but":
                continue
            if word not in invertedIndex:
                print(word + " not a valid entry")
                return word

def webSearch(invertedIndex, docTable, searchEntry):
    """
    Web engine console.
    :param invertedIndex: Inverted index table.
    :param docTable: Table containing doc information
    :return:
    """
    resultsDictionary = {}

    # Check for phrasal first.
    if "\"" in searchEntry:
        print("Preforming phrasal search...")

        try:
            # Initial Phrasal Search
            top_docs, query = searchFunctions.phrasalSearch(searchEntry, invertedIndex, docTable)
            top_docs = np.unique(top_docs,axis=0).tolist()
            top_docs = sorted(top_docs, key=rankBySecondElem, reverse=True)

            # extract top correlated words, ignoring stop words.
            top_correlated_words = correlations.wordBasedCorrelation(inverted_index, query, top_docs, docTable)

            # extract documents that match top correlated words (using or function by default)
            top_docs_CorreKeys, querySecondRun = searchFunctions.booleanSearch(top_correlated_words, invertedIndex,
                                                                               docTable)

            correlated_Docs = correlations.docBasedCorrelation(docTable, top_docs)

            resultsDictionary["Top Documents"] = top_docs[:25]
            resultsDictionary["Top Docs With Correlated Keys"] = top_docs_CorreKeys[:20]
            resultsDictionary["Top Docs With Correlated Docs"] = correlated_Docs[:20]

            return resultsDictionary
        except:
            print("Returned None - Your query contains invalid entry. See above.")


    elif len(searchEntry.split()) == 1:
        print("Only searching for one word...")

        try:
            # Initial Boolean Search
            top_docs, query = searchFunctions.booleanSearch(searchEntry, invertedIndex, docTable)

            # extract top correlated words, ignoring stop words.
            top_correlated_words = correlations.wordBasedCorrelation(inverted_index, query, top_docs, docTable)

            # extract documents that match top correlated words (using or function by default)
            top_docs_CorreKeys, querySecondRun = searchFunctions.booleanSearch(top_correlated_words, invertedIndex,
                                                                               docTable)

            correlated_Docs = correlations.docBasedCorrelation(docTable, top_docs)

            resultsDictionary["Top Documents"] = top_docs
            resultsDictionary["Top Docs With Correlated Keys"] = top_docs_CorreKeys
            resultsDictionary["Top Docs With Correlated Docs"] = correlated_Docs

            return resultsDictionary

        except:
            print("Returned None - Your query contains invalid entry. See above.")

    else:
        print("Preforming boolean search...")
        try:
            # Initial Boolean Search
            top_docs, query = searchFunctions.booleanSearch(searchEntry, invertedIndex, docTable)
            top_docs = np.unique(top_docs, axis=0).tolist()
            top_docs = sorted(top_docs, key=rankBySecondElem, reverse=True)
            # extract top correlated words, ignoring stop words.
            top_correlated_words = correlations.wordBasedCorrelation(inverted_index, query, top_docs, docTable)

            # extract documents that match top correlated words (using or function by default)
            top_docs_CorreKeys, querySecondRun = searchFunctions.booleanSearch(top_correlated_words, invertedIndex,
                                                                               docTable)

            correlated_Docs = correlations.docBasedCorrelation(docTable, top_docs)

            resultsDictionary["Top Documents"] = top_docs[:25]
            resultsDictionary["Top Docs With Correlated Keys"] = top_docs_CorreKeys[:20]
            resultsDictionary["Top Docs With Correlated Docs"] = correlated_Docs[:20]

            return resultsDictionary

        except:
            print("Returned None - Your query contains invalid entry. See above.")


## Build app.
app = Flask(__name__)
@app.route('/')
@app.route('/home')
def home():
    print("inverted Index")
    #print(inverted_index)
    return render_template('mainPage.html')

@app.route('/result', methods =['POST', 'GET'])
def result():
    output = request.form.to_dict()
    searchKeys = output["query"]
    results_to_print = webSearch(inverted_index, document_table, searchKeys)

    badWord = ""
    if results_to_print is None:
        results_to_print = {}
        results_to_print["Top Documents"] = ["Not Available"]
        results_to_print["Top Docs With Correlated Keys"] = ["Not Available"]
        results_to_print["Top Docs With Correlated Docs"] = ["Not Available"]
        badWord = checkIndexFrontPage(searchKeys, inverted_index)
    else:
        for key, value in results_to_print.items():
            results_to_print[key] = [entry + [document_table[entry[0]]['short description']] for entry in value]

    return render_template("mainPage.html", queryEntry=searchKeys, results_to_print=results_to_print, badWord=badWord)

if __name__ == '__main__':

    buildIndexTables()

    app.run(debug=True, port=5000)

    #correlations.docBasedCorrelation(document_table)


