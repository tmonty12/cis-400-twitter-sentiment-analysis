import json
import re

import nltk
import pandas as pd

from nltk.probability import FreqDist
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords


class SentimentAnalysis:
    def __init__(self):
        self.tweets = None
        self._load()

    # load tweets from a json file
    def _load(self, path="data/tweets.json"):
        with open(path, "r") as f:
            data = json.loads(f.read())['data']
        self.tweets = pd.json_normalize(data)

    # return the top 5 words from a set of tweets
    def top5words(self):
        # prepare tweets by stripping out links and punctuation
        self.tweets['cleantext'] = self.tweets['text'].apply(SentimentAnalysis.cleanText)
        tokens = []
        for tweet in self.tweets['cleantext'].values:
            # filter out stopwords
            tokens += [word for word in nltk.word_tokenize(tweet) if word not in stopwords.words('english')]
        # return top 5 words
        return [word[0] for word in FreqDist(tokens).most_common(5)]

    # compute the reputation score for the user. Score is the average
    # reputation score of all tweets referencing the user
    def reputation_score(self):
        self.tweets['reputationscore'] = self.tweets['text'].apply(SentimentAnalysis._reputation_score)
        return self.tweets['reputationscore'].mean()

    # compute the reputation score for a tweet.
    # Reputation score = (pos-neg)*comp
    # Score range [-1, 1]
    @staticmethod
    def _reputation_score(s):
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(s)
        return (scores['pos']-scores['neg'])*scores['compound']

    # remove non-letters, links and "rt" notation from tweets
    @staticmethod
    def cleanText(s):
        # remove rt notation and links
        s = str(s).lower().replace('rt ', '')
        s = re.sub(r'https?:\/\/\S+', '', s)
        # remove non-letters
        s = re.sub(r'[^a-zA-Z\s]', '', s)
        return s

# testing

# sa = SentimentAnalysis()
# print(sa.top5words())
# print(sa.reputation_score())
