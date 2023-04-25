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
        self.username = ''

    # load tweets from a json file
    def _load(self, path="../data/tweets.json"):
        with open(path, "r") as f:
            data = json.loads(f.read())['data']
        self.tweets = pd.json_normalize(data)

    # loads tweets passed from Twitter API to class
    def load_tweets(self, tweets, username):
        self.tweets = pd.DataFrame({
            'text': tweets
        })
        self.username = username

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
    
    def top5usernames(self):
        self.tweets['usernames'] = self.tweets['text'].apply(SentimentAnalysis.grabUsernames)
        freqDist = FreqDist()
        for usernames in self.tweets['usernames'].values:
            for username in usernames:
                freqDist[username.lower()] += 1
        print(self.username)
        freqDist.pop(self.username)
        return [word[0] for word in freqDist.most_common(5)]
                

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
        s = re.sub(r'@\w{1,15}(?!\w)', '', s)
        # remove non-letters
        s = re.sub(r'[^a-zA-Z\s]', '', s)
        return s
    
    @staticmethod
    def grabUsernames(s):
        return re.findall(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)', s)
