import re
import os

def clean_corpus(path):
    filelist = os.listdir(path)
    cleaned_corpus = []
    for i in filelist:
        cleaned_corpus.append(remove_brackets(path + i))
    #cleaned_corpus = remove_non_message_text(file)
    return cleaned_corpus

def remove_brackets(file):
    #pattern = r"\[.*?\]"
    with open(file, "r", encoding='utf-8') as corpus_file:
        content = corpus_file.read()
    pattern = r"\[.*?\]"
    cleaned_corpus = re.sub(pattern, "", content)
    pattern = r"\(.*?\)"
    cleaned_corpus = re.sub(pattern, "", content)
    return cleaned_corpus
    #return tuple(cleaned_corpus.split("\n"))
    #return tuple((msg for msg in messages if msg not in filter_out_msgs))
