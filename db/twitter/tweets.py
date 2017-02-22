import tweepy
import re
from config import (PUBLIC_API_KEY,
                    SECRET_API_KEY,
                    PUBLIC_ACCESS_TOKEN,
                    SECRET_ACCESS_TOKEN)
from tweepy.streaming import StreamListener
from tweepy import (OAuthHandler,
                    Stream)

emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""


regex_str = [
    r'(?:@[\w_]+)', # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    r'\$[A-z]{1,4}', # ticker sybols
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs
    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    r'(?:[\w_]+)', # other words
]


tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)

def tokenize(tweet, lowercase=False):
    tokens = tokens_re.findall(tweet)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens



class StdOutListener(StreamListener):

    def on_status(self, status):
        print( tokenize(status.text) )
        return True # keep listening

    def on_error(self, status):
        print(status)
        return True # keep listening

    def on_timeout(self):
        return True # keep listening





if __name__ == "__main__":

    l = StdOutListener()
    auth = OAuthHandler(PUBLIC_API_KEY, SECRET_API_KEY)
    auth.set_access_token(PUBLIC_ACCESS_TOKEN, SECRET_ACCESS_TOKEN)
    myStream = Stream(auth, StdOutListener())
    myStream.userstream(encoding='utf8')
