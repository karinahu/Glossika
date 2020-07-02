import nltk
from nltk.corpus import wordnet as wn
import spacy
from spacy.lang.en import English
import csv

"""
input: noun phrases
"""
nlp = spacy.load('en_core_web_lg')
wordlist = []
def PathtoCsv(file_path):
    """
    input: given a txt file of noun phrases
    output: a csv file of the hypernym paths
    """
    with open(file_path, 'r') as File:
        lines = File.readlines()
        for line in lines:
            wordlist.append(line.rstrip())
    # print(wordlist[:3])
    # deal with multi-lemma word
    with open ('NP_semantic_paths.csv', 'w', newline = '') as path_file:
        writer = csv.writer(path_file, delimiter = ',')
        for word in wordlist:
            # if word contains space, meaning if it is a multi-lemma word
            if " " in word:
                word = word.replace(" ", "_")
            synset = BestSynset(word)
            try:
                # string processing to get the name of the synset
                upper_path = wn.synset(str(synset)[8:-2]).hypernym_paths()
                # print("Path:", upper_path[0])
                # hypernym_paths() returns a list of path(s)
                for path in upper_path:
                    # list comprehension
                    result = [str(synset)[8:-7]for synset in path]
                    # print(result[:2])
                    # insert這行可以改良
                    # signal which word the path starts in index 0 in result
                    result.insert(0, word.replace("_"," "))
                    writer.writerow(result)
            except:
                # BestSynset returns [Ner], can't be processed as a synset
                if synset:
                    ner = synset
                    ner.insert(0, word.replace("_"," "))
                    writer.writerow(ner)
                # BestSynset returns None
                else:
                    x = ['No tag avaliable']
                    x.insert(0, word.replace("_"," "))
                    writer.writerow(x)

def BestSynset(word):
    word = word.lower()
    synset_list = wn.synsets(word)
    # take the whole word and feed it into wordnet
    # case1: if the init list is huge
    if len(synset_list) > 1:
        for synset in synset_list:
            if word == 'cosigner':
                # return 'cosiner.n.02'
                return synset_list[1]
            if str(synset)[8:-2] == "%s.n.01"%word:
                return synset
            if word in str(synset):
                return synset
            else:
                # british spelling
                return synset_list[0]
    # case2: if the init list only contains one synset
    elif len(synset_list) == 1:
        # return the only synset
        return synset_list[0]
    # case3: if wordnet returns empty list
    else:
        # if the init list is empty and the word is a multi-lemma word
        if "_" in word:
            # exception handling
            if word == "international_labor_day":
                synset_list = wn.synsets('labor_day')
                return synset_list[0]
            elif word == 'forwarding_agent':
                synset_list = wn.synsets('agent')
                for synset in synset_list:
                    if str(synset)[8:-2] == "agent.n.02":
                        return synset
            elif word == 'mainland_china':
                # Synset('china.n.01')
                return synset[0]
            # use head (possible pos is [-1])
            word = word.split("_")[-1]
            synset_list = wn.synsets(word)
            # if the list only contains one synset
            if len(synset_list) == 1:
                # return the only synset
                return synset_list[0]
            elif len(synset_list) > 1:
                for synset in synset_list:
                    if str(synset)[8:-2] == "%s.n.01"%word:
                        return synset
                    if word in str(synset):
                        return synset
                return synset_list[0]
        # if the word is a NAMED ENTITY
        elif word in ['amazon(amzn)', 'instagram', 'facebook', 'glossika', 'dropbox', 'whatsapp', 'microsoft', 'snapchat', 'obama', 'elon musk', 'samsung', 'starbucks']:
            if word in ['amazon(amzn)', 'facebook', 'whatsapp', 'snapchat']:
                return ['NERs that don\'t have defined tags']
            return Ner(word) # [Ner] it's in a list form
    # wordnet returns empty synset list
def Ner(word):
    """
    if wordnet fail to return a satisfactory result, return ner tags from spacy
    supported entity categories on spacy:
    https://spacy.io/api/annotation#named-entities
    """
    doc = nlp(word)
    return [ent.label_ for ent in doc.ents]
PathtoCsv('wordlist.txt')

