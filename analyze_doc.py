# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 14:23:41 2012

@author: du
"""

import unicodedata
import MeCab
import re

non_ascii = re.compile(r'[^\x20-\x7E]')
tagger = MeCab.Tagger("mecabrc")
url_pattern = re.compile(r"[a-zA-Z]+://[^\s]+")

def filter_f(w):
    length = len(w)
    if length < 2 :
        return False
    if non_ascii.search(w) == None and length < 3:
        return False
    if w[0] == ".":
        return False
    return True
    
def normalize_char(s):
    s = unicodedata.normalize("NFKC", s).lower()
    return s

def parseWords(doc):
    node = tagger.parseToNode(doc)
    words = []
    while node:
        word_type = node.feature.split(",")[0]
#        if word_type in ("名詞", "形容詞", "動詞"):
        if word_type in ("名詞", "形容詞"):
            words.append(node.surface)
        node = node.next
    words = [w.decode("utf-8") for w in words]
    return filter(filter_f, words)
    #return words        
        
def ngram(words, n=2):
    return [" ".join(words[i:i+n]) for i in xrange(len(words)-(n-1))]
    
def neighborWords(words, target, length=3):
    n = words.count(target)
    neighbor = []
    idx = -1
    n_words = len(words)
    for nn in xrange(n):
        idx = words.index(target,idx+1)
        neighbor.extend(words[max(0, idx-length):min(idx+length+1, n_words)])
    return neighbor
    
def main(db_name, keyword):
    import sqlite3
    
    db = sqlite3.connect(db_name)
    #res = db.execute("select title from BLOG_DATA").fetchall()
    res = db.execute("select text from TWEET_DATA").fetchall()
    docs = []
    for e in res:
        doc = url_pattern.sub("", normalize_char(e[0])).encode("utf-8")
        docs.append(doc)
    
    words = map(parseWords, docs)
    bigrams = reduce(lambda x, y: x + ngram(y, 2), words, []) 
#    neighbors = reduce(lambda x, y: x + neighborWords(y, keyword, 2), words, [])         
        
    return docs, bigrams

