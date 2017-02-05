"""
Implementation of TextRank, as described in this paper:
    https://web.eecs.umich.edu/~mihalcea/papers/mihalcea.emnlp04.pdf
Steps:
-------------------------------------------------------------------------------
1. Identify text units (words, sentences) that best define the task at hand
   and add them as vertices in the graph.

2. Identify relations that connect such text units, and use these relations to
   draw edges between vertices to draw edges between vertices in the graph.
      *levenshtein distance, co-occurence, # similar words, etc.

3. Iterate the graph-based ranking algortihm until convergence.

4. Sort vertices based on the final score. Use the value attatched to each vertex
   for ranking/selection decisions.
-------------------------------------------------------------------------------
"""
import itertools
import networkx
from collections import Counter
from gfnews import _get_articles
from math import log10, floor
from nltk.tokenize import sent_tokenize, word_tokenize
from newspaper import Article

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


def _sentence_overlap(s1, s2):
    """
    Returns the number of common tokens between two sentences. To avoid promoting
    long sentences, a normalization factor is applied by dividing the contence overlap
    of two sentences with the length of each sentence.
    """
    words1, words2 = _tokenize_words(s1), _tokenize_words(s2)
    seen = {word for word in words1}
    overlap = sum(1 for w in words2 if w in seen)
    norm = log10(len(s1)) + log10(len(s2))
    return overlap / norm


def _tokenize_words(text):
    words = word_tokenize(text)
    return [word.strip().replace('\n', '') for word in words]


def _tokenize_sentences(text):
    """
    Split text into sentences, using NLTK tokenizer.
    """
    import nltk.data
    # pre-trained Punkt tokenizer for English
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = sent_detector.tokenize(text.strip())
    return [ sentence.replace('\n', ' ') for sentence in sentences ]


def _build_graph(textUnits, key):
    """
    Leverages networkx to build a graph from the textUnits, and uses the provided
    key to detmine what weight function to use.
    """
    G = networkx.Graph()
    G.add_nodes_from(textUnits)
    weightFunc = _levenshtein_dist if key=='levanshtein' else _sentence_overlap
    # draw weighted edge between every textUnit
    for s1, s2 in itertools.combinations(textUnits, 2):
        weight = weightFunc(s1, s2)
        G.add_edge(s1, s2, weight=weight)

    return G

def extractKeywords(text, coocc=2, key='levanshtein'):
    """
    Tokenizes the text into words, then runs the TextRank algorithm.
    """
    words = set(_tokenize_words(text))
    # nouns & adjectives got best results, so filter using NLTK part-of-speech tagger
    wordsAndTags = nltk.pos_tag(words)
    adjAndNounTags = ['JJ', 'JJR', 'JJS', 'NN', 'NNS', 'NNP']

    return words



def extractSummary(url, keep=0.2, key='levanshtein'):
    """
    Tokenizes the text into sentences, then runs TextRank algorithm. The sentences
    will be ranked according to the key passed in, and the amount of sentences
    returned will depend on the keep parameter. The default is 0.2, which will
    cut the text down by 80%.

    Parameters:
        text (str): text to summarize
        keep (int): ratio of sentences to keep from the summary
        key (str): metric used to determine rank
            either `levanshtein` or `overlap`
    """
    if keep < 0 or keep > 1:
        raise ValueError("keep must be in the range [0,1]")
    if key not in ['levanshtein', 'overlap']:
        raise ValueError('key must be either `levanshtein` or `overlap`')
    article = Article(url)
    article.download()
    if article.is_downloaded:
        article.parse()
    else:
        return ''
    # tokenize text, and keep chronological o
    sentences = _tokenize_sentences(article.text)
    locs = {sentence:i for i, sentence in enumerate(sentences)}
    G = _build_graph(sentences, key)
    textRank = networkx.pagerank(G, weight='weight')

    topSentences = sorted(textRank, key=textRank.get, reverse=True)
    numToKeep = floor(keep * len(sentences))
    # map each sentence to it's original location in the text
    summary = [ (sentence,locs[sentence]) for sentence in topSentences[:numToKeep]]
    # sort by chronological order
    summary.sort(key=lambda t: t[1])

    return ' '.join(t[0] for t in summary)

