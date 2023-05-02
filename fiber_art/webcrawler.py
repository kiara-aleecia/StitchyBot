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
    starter_url = 'https://en.wikipedia.org/wiki/Fiber_art'

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
    ignore = ['SMarcus', 'worldcat', 'britannica', 'Shaw', 'b016vxz1', 'er.2019.06',
              'nytimes', 'artsy-editorial', 'profile', 'royal-needlework', 'aaa.si.edu',
              'fiberartnow', 'intelligencer', 'textilemuseum', 'textileartist', 'blackartinamerica',
              ]
    is_ignored = False
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
    
    # substantial_urls.remove(3)
    # substantial_urls.remove(64)
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
    #print(f"index of crochet: {[index for (index, tup) in enumerate(doc_term_weights) if 'crochet' in tup[0]]}")
    print("\nMost important: ", doc_term_weights[:100])

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

        # only find 5 sentences for each word
        for s in sentences:
            base_length = 5
            for w in vip:
                knowledge_base.setdefault(w, [])
                if w in s and base_length > 0:
                    knowledge_base[w].append(s)
                    base_length -= 1
    #print(knowledge_base)
    # for t in knowledge_base:
    #     print(t + "\n\n\n\n")
    #     print(knowledge_base[t])


'''
function driver and where we manually pick important terms and handpick
important sentences for knowledge base -> pickled
'''
def main():
    webcrawler()
    filecount = webscraper()
    #filecount = 95
    filecount, significant = cleanup(filecount)
    important_terms(significant)
    # manually determine the top 10 terms based on your domain knowledge
    # build searchable knowledge base of facts related to the 10 terms for a chatbot
    #most_important = ['larvae', 'zooplanktonic', 'stomatopods', 'adult', 'overtly', 
    #                  'persists', 'equator', 'sympatric', 'photoreceptor', 'reabsorbed']
    most_important = []
    # find all sentences containing the most important terms
    # create_knowledge_base(most_important, significant)

    # manually clean up knowledge base
    knowledge_base = {
        'larvae': ['stomatopod larvae lack the unusual, specialized ocular features of adults—and instead possess compound eyes similar to those of other zooplanktonic crustacean larvae',
                   'it has been reported that larval behavior, specifically maximum depth range for vertical migration, changes as stomatopods progress from early to late stages of larval development',
                   'hatched larvae had a prominent yolk sac which was fully absorbed around 50 days post-hatching',
                   'larvae have stemmata and adults have compound eyes',
                   'firefly larvae, like adults, are bioluminescent, but unlike adults, they do not rely on their visual systems for the reception and processing of flash patterns'
                   ], 
        'zooplanktonic': ['given that larvae perform many of the same generic zooplanktonic behaviors (i.e., feeding, vertical migrations, predator avoidance), we hypothesized that sympatric species possess similar visual pigment absorption spectra that are tuned to the pelagic light environment.',
                          'stomatopod larvae lack the unusual, specialized ocular features of adults—and instead possess compound eyes similar to those of other zooplanktonic crustacean larvae'
                          ], 
        'stomatopods': ['our understanding of the visual pigment diversity of larval stomatopods, however, is based on four species, which severely limits our understanding of stomatopod eye ontogeny.',
                        'stomatopods are known for the elaborate visual systems found in adults of many species.',
                        'behavioral evidence also indicates that stomatopods are capable of discriminating objects by their spectral differences alone.',
                        'most animals use only two to four different types of photoreceptors in their color vision systems, typically with broad sensitivity functions, but the stomatopods apparently include eight or more narrowband photoreceptor classes for color recognition.'
                        ], 
        'adult': ['chromophore usage and light sensitivity shift across ontogenychanges in visual pigment light sensitivity associated with the use of the a1 and/or a2 chromophores have been established using spectrophotometry of retinal extracts and msp of intact photoreceptors in several tadpole and adult frogs',
                  'adult stomatopod eyes have the largest reported photoreceptor diversity in a single eye, which in some species can include up to 16 classes of photoreceptors',
                  'larval stomatopod eyes appear to be much simpler versions of adult compound eyes, lacking most of the visual pigment diversity and photoreceptor specializations.'
                  ], 
        'overtly': ['the stark differences between larval and adult stomatopod eye structures do not become overtly apparent until metamorphosis.'
                    ], 
        'persists': ['in the final hours of the terminal larval stage, the adult retina develops completely separate from, but adjacent to, the preexisting larval eye tissue and persists into the juvenile adult stage until the larval tissue is completely pushed aside and reabsorbed'
                    ], 
        'equator': ['many of these specialized receptor classes are found in the six rows of often enlarged ommatidia that run along the equator of many adult eyes, referred to as the midband.'
                    ], 
        'sympatric': ['rather, there was significant variation in visual pigment absorption spectra among sympatric species.', 
                       'previous microspectrophotometric studies sampled stomatopod larvae procured from different locations; thus, photoreceptor variation among sympatric larvae remains unknown.', 
                       'given that larvae perform many of the same generic zooplanktonic behaviors (i.e., feeding, vertical migrations, predator avoidance), we hypothesized that sympatric species possess similar visual pigment absorption spectra that are tuned to the pelagic light environment', 
                       'detailed discussions of each of these findings are provided below.using msp, we characterized photoreceptor spectral absorption in eight sympatric species of stomatopod larvae, six of which were previously uncharacterized', 
                       'though some species matched our prediction, visual pigments in three of the sampled species maximally absorbed at wavelengths significantly shorter than those of their sympatric heterospecifics, leading us to reject our initial hypothesis that larval species in the same habitat share similar visual pigment absorption spectra.', 
                       'until more is known regarding stomatopod larval ecology and behavior, the adaptive significance of different photoreceptor classes in each species will remain unknown.though differences in ecology offer a potential explanation for the unexpected variation in the λ max values of sympatric species, an alternate hypothesis that considers the developmental stages of sampled individuals may also explain these results.'
                       ],
        'photoreceptor': ['previous microspectrophotometric studies sampled stomatopod larvae procured from different locations; thus, photoreceptor variation among sympatric larvae remains unknown.',
                           'until more is known regarding stomatopod larval ecology and behavior, the adaptive significance of different photoreceptor classes in each species will remain unknown.'
                           ], 
        'reabsorbed': ['in the final hours of the terminal larval stage, the adult retina develops completely separate from, but adjacent to, the preexisting larval eye tissue and persists into the juvenile adult stage until the larval tissue is completely pushed aside and reabsorbed'
                       ]

    }
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