# Homework 8
# Crystal Ngo and Kiara Madeam
# https://github.com/cmn180003/NLP-Portfolio
# https://github.com/kiara-aleecia/nlp-portfolio

from bs4 import BeautifulSoup
import requests
#import urllib
from urllib import request
import os
import re
import nltk
from nltk import word_tokenize
from nltk import sent_tokenize
from nltk.corpus import stopwords
import math
import pickle
import shutil

'''
TO DO:
[X]- start with url representing a topic
[X]- output a list of at least 15 relevant urls
[X]- write function to loop through urls and scrape all text off each page
[X]- store each page's text in its own file
[X]- write function to clean up text from each file
    [X]- delete newlines and tabs
    [X}- extract sentences with nltk sentence tokenizer
    [X]- write sentences for each file to a new file (15 in, 15 out)
[X]- write a function to extract at least 25 important terms
    [X]- use term frequency or tf-idf
    [X]- first lowercase everything, remove stopwords, remove punctuation
    [X]- print top 25-40 terms
[X]- manually determine the top 10 terms based on your domain knowledge
[X]- build searchable knowledge base of facts related to the 10 terms for a chatbot
    [X]- can be as simple as a pickled python dictionary
- complete write up
- link to portfolio on github
'''

'''
[X]- start with url representing a topic
[X]- output a list of at least 15 relevant urls
'''
def webcrawler():
    starter_url = 'https://en.wikipedia.org/wiki/Knitting'

    r = requests.get(starter_url)

    data = r.text
    soup = BeautifulSoup(data, features='html.parser')

    # write urls to a file
    with open('urls.txt', 'w') as f:
        f.write(starter_url + '\n')
        for link in soup.find_all('a'):
            link_str = str(link.get('href'))
            print(link_str)
            if link_str.startswith('/url?q='):
                link_str = link_str[7:]
                print('MOD:', link_str)
            if '&' in link_str:
                i = link_str.find('&')
                link_str = link_str[:i]
            if link_str.startswith('http') and 'google' not in link_str:
                if 'wikipedia' in link_str and 'en.' not in link_str:
                    continue
                f.write(link_str + '\n')

    # end of function
    f.close()
    print("end of crawler")

'''
[X]- write function to loop through urls and scrape all text off each page
[X]- store each page's text in its own file
'''
def webscraper():
    file = open('urls.txt', 'r')
    urls = file.readlines()
    count = 1

    # ignore links that we cannot access    
    ignore = ['jstor', 'wor222lds', 'worldcat', 'alamacknits', '93180136', 'nytimes',
              'knittinghelp', 'carolmilne', 'pdxmonthly', 'anneliesdekort',
              'rosecityyarncrawl', 'yarncrawlnyc', 'glyc-2016', 'triangleyarncrawl',
              'tct.org.au', 'Hensandtheirjumpers', 'projectlinus', 'ncbi.nlm.nih', '10.1176',
              'bytomdaley', 'cafeknit', 'id.ndl.go.jp']
    #is_ignored = False
    # Creates files of all text from all urls
    for url in urls:
        for i in ignore:
            if i in url:
                is_ignored = True
                break
            # if 'wikipedia' in url and 'en.' not in url:
            #     is_ignored = True
            #     break
            else:
                is_ignored = False

        if not is_ignored:
            print(url)
            html = request.urlopen(url).read().decode('utf8')
            soup = BeautifulSoup(html, features='html.parser')

            # kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()  # rip it out

            # extract text, writes text to new file
            text = soup.get_text()
            newfile = open('url/url' + str(count) + '.txt', 'w', encoding="utf-8")
            newfile.writelines(text[:])
            newfile.close()
            if os.path.getsize('url/url' + str(count) + '.txt') < 10000:
                os.remove('url/url' + str(count) + '.txt')
        count += 1
    print(f'fileamnt is {count-1}')
    return count - 1

'''
[X]- write function to clean up text from each file
    [X]- delete newlines and tabs
    [X]- extract sentences with nltk sentence tokenizer
    [X]- write sentences for each file to a new file (15 in, 15 out)
'''
def cleanup(fileamnt):
    #remove files we don't need
    words = set(nltk.corpus.words.words())
    

    substantial_urls = []
    for i in range(1, fileamnt+1):
        curr_file = 'url/url' + str(i) + '.txt'
        if os.path.exists(curr_file):
            fi = open(curr_file, 'r+', encoding='utf8')
            file_words = fi.read()
            file_words = nltk.wordpunct_tokenize(file_words)
            file_words = " ".join(w for w in file_words)
            fi.writelines(file_words[:])
            fi.close()
            if os.path.getsize(curr_file) < 10000:
                os.remove(curr_file)
                continue
            substantial_urls.append(i)
    
    substantial_urls.remove(3)
    substantial_urls.remove(64)
    print('done removing unnecessary files!!')
    print(substantial_urls)

    for url in substantial_urls:
        filepath = 'url/url' + str(url) + '.txt'
        file = open(filepath, 'r', encoding='utf8').read()
        text = " ".join(file.split())
        #print(text)
        filepath = 'url/clean' + str(url) + '.txt'

        file = open(filepath, 'w', encoding="utf-8")
        file.writelines(text[:])
        file.close()
        shutil.move(filepath, 'cleandata/clean' + str(url) + '.txt')

    return len(substantial_urls), substantial_urls

'''
[X]- write a function to extract at least 25 important terms
    [X]- use term frequency or tf-idf
    [X]- first lowercase everything, remove stopwords, remove punctuation
    [X}- print top 25-40 terms
'''
def important_terms(substantial_urls):
    total_terms = []
    vocab_by_topic = []
    # needs to be a list of dictionaries
    tf_dict_list = []
    tf_dict = {}
    idf_dict = {}

    #Gets tf for all files
    for url in substantial_urls:
        #Gets file ready for extraction
        filepath = ('cleandata/clean' + str(url) + '.txt')
        file = open(filepath, 'r', encoding='utf8').read()
        file = re.sub(r'[.?!,:;()\-\n\d]', ' ', file.lower())
        
        #remove nonenglish
        words = set([w.lower() for w in nltk.corpus.words.words('en')])
        tokens = word_tokenize(file)
        tokens = [w for w in tokens if w in words]

        #Removes stopwords
        stpwrds = set(stopwords.words('english'))
        tokens = [t for t in tokens if not t in stpwrds]

        # add to list of vocab for all files
        total_terms.append(tokens)

        print(len(tokens))
        #tf_dict = {t: tokens.count(t) for t in token_set}
        tf_dict = {t: tokens.count(t) for t in tokens}
        
        #Normalize tf by number of tokens
        for t in tf_dict.keys():
            tf_dict[t] = tf_dict[t] / len(tokens)
    
        tf_dict_list.append(tf_dict)
        vocab_by_topic.append(list(tf_dict.keys()))

    #Gets idf
    for section in vocab_by_topic:
        for term in section:
            temp = ['x' for voc in vocab_by_topic if term in voc]
            idf_dict[term] = math.log((1+len(substantial_urls)) / (1+len(temp)))

    #Get tf-idf for all files
    tf_idf = {}
    for t_dict in tf_dict_list:
        for t in t_dict:
            tf_idf[t] = tf_dict.get(t, 1) * idf_dict.get(t, 1)

    #Prints top 25 words
    #doc_term_weights = sorted(tf_idf.items(), key=lambda x: x[1], reverse=True)
    doc_term_weights = sorted(tf_dict.items(), key=lambda x: x[1], reverse=True)
    print(f"imp terms length: {len(doc_term_weights)}")
    print(f"index of knit: {[index for (index, tup) in enumerate(doc_term_weights) if 'knit' in tup[0]]}")
    print("\nMost important: ", doc_term_weights[:120])

'''
[X]- build searchable knowledge base of facts related to the 10 terms for a chatbot
    - can be as simple as a pickled python dictionary
'''
def create_knowledge_base(vip, substantial_urls):
    knowledge_base = {}
    for url in substantial_urls:
        filepath = ('cleandata/clean' + str(url) + '.txt')
        file = open(filepath, 'r', encoding='utf8').read().lower()
        sentences = sent_tokenize(file)

        # only find 10 sentences for each word
        for s in sentences:
            base_length = 10
            for w in vip:
                knowledge_base.setdefault(w, [])
                if w in s and base_length > 0:
                    knowledge_base[w].append(s)
                    base_length -= 1
    #print(knowledge_base)
    for t in knowledge_base:
        filepath = 'kb_texts/' + t + '.txt'
        file = open(filepath, 'w', encoding="utf-8")
        for l in knowledge_base[t]:
            file.writelines(l + '\n\n')
        file.close()
    # for t in knowledge_base:
    #     print(t + "\n\n\n\n")
    #     print(knowledge_base[t])


'''
function driver and where we manually pick important terms and handpick
important sentences for knowledge base -> pickled
'''
def main():
    #webcrawler()
    #filecount = webscraper()
    #filecount = 95
    #filecount, significant = cleanup(filecount)
    significant = [1, 5, 8, 24, 26, 29]
    #important_terms(significant)
    # manually determine the top 10 terms based on your domain knowledge
    # build searchable knowledge base of facts related to the 10 terms for a chatbot
    #most_important = ['larvae', 'zooplanktonic', 'stomatopods', 'adult', 'overtly', 
    #                  'persists', 'equator', 'sympatric', 'photoreceptor', 'reabsorbed']
    most_important = ['knit', 'yarn', 'pattern', 'needle', 'dominant', 'loop', 'tension', 'purl',
                      'loom', 'cable', 'stitch', 'product', 'cast', 'style', 'hand',
                       'art', 'garment', 'row', 'purl', 'textile', 'century', 'yarn']
    # find all sentences containing the most important terms
    create_knowledge_base(most_important, significant)

    # manually clean up knowledge base
    # knowledge_base = {}
    # print("KNOWLEDGE BASE:\n\n")
    # for t in knowledge_base:
    #     print(t)
    #     print(knowledge_base[t])
    #     print("\n\n\n\n")

    # pickle the knowledge base
    # pickle.dump(knowledge_base, open('knowledge_base.pickle', 'wb'))


# Starts program
if __name__ == '__main__':
    main()