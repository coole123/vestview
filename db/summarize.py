"""
Implementation of TextRank, as described in this paper:
    https://web.eecs.umich.edu/~mihalcea/papers/mihalcea.emnlp04.pdf
"""
import re
from collections import Counter
from bs4 import BeautifulSoup
from gfnews import _get_articles
from nltk.tokenize import sent_tokenize, word_tokenize

def _levenshtein_dist(s1, s2):
    """
    Returns the levenshtein distance (min # of insertions, deletions, and replacments)
    between two sentences. This implements a bottom-up dynamic programming approach,
    optimized for memory.
    """
    # if sentences, want to split into words
    s1, s2 = s1.split(' '), s2.split(' ')
    (s1 , s2) = (s2, s1) if len(s1) > len(s2) else (s1, s2)

    prevRow = range(len(s2) + 1)

    for j, c2 in enumerate(s2):
        currRow = [j + 1]
        for i, c1 in enumerate(s1):
            if c1 == c2:
                currRow.append(prevRow[i])
            else:
                currRow.append(1 + min((prevRow[i],
                                        prevRow[i + 1],
                                        currRow[-1])))
        prevRow = currRow

    return prevRow[-1]

def _tokenize_sentences(text):
    """
    Split text into sentences, using NLTK tokenizer.
    """
    import nltk.data
    # pre-trained Punkt tokenizer for English
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = sent_detector.tokenize(text.strip())
    return [ sentence.replace('\n', '') for sentence in sentences ]

