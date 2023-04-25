import json
import re

import nltk
import pandas as pd

from nltk.probability import FreqDist
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tag.stanford import StanfordNERTagger

import contractions


class SentimentAnalysis:
    def __init__(self):
        self.tweets = None

    # load tweets from a json file
    def load_tweets_from_file(self, path="../data/tweets.json"):
        with open(path, "r") as f:
            data = json.loads(f.read())['data']
        self.tweets = pd.json_normalize(data)

    # loads tweets passed from Twitter API to class
    def load_tweets(self, tweets):
        self.tweets = pd.DataFrame({
            'text': tweets
        })

    # return the top 5 words from a set of tweets
    def top5words(self):
        contracts = [word.replace("'", '') for word in list(contractions.contractions_dict.keys())]
        # prepare tweets by stripping out links and punctuation
        self.tweets['cleantext'] = self.tweets['text'].apply(SentimentAnalysis.cleanText)
        tokens = []
        for tweet in self.tweets['cleantext'].values:
            # filter out stopwords and contractions
            tokens += [word for word in nltk.word_tokenize(tweet) if word.lower() not in
                       stopwords.words('english') + contracts]
        # filter out non-nouns
        tokens = [word[0] for word in nltk.pos_tag(tokens) if word[1] in ['NN', 'NNS', 'NNP']]
        # initialize NERTagger
        st = StanfordNERTagger('data/stanford-ner/english.all.3class.distsim.crf.ser.gz',
                               'data/stanford-ner/stanford-ner-4.2.0.jar')
        # tag tokens
        tags = st.tag(tokens)
        # filter to tokens tagged with PERSON
        tags = set([tag[0].lower() for tag in tags if tag[1] in ['PERSON']])
        # remove from list
        tokens = [word for word in tokens if word.lower() not in tags]
        # return top 5 words
        return [word[0] for word in FreqDist(tokens).most_common(5)]

    # compute the reputation score for the user. Score is the average
    # reputation score of all tweets referencing the user
    def reputation_score(self):
        self.tweets['reputationscore'] = self.tweets['text'].apply(SentimentAnalysis._reputation_score)
        return SentimentAnalysis.map_score(self.tweets['reputationscore'].mean())

    # compute the reputation score for a tweet.
    # Score range [-1, 1]
    @staticmethod
    def _reputation_score(s):
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(s)
        return scores['compound']

    @staticmethod
    def map_score(score):
        mn1, mx1 = -0.2, 0.2
        mn2, mx2 = 1, 100
        c = SentimentAnalysis.clamp(mn2, mx2)
        return c((mx2 - mn2) * (score - mn1) / (mx1 - mn1) + mn2)

    @staticmethod
    def clamp(mn, mx):
        return lambda value: max(min(value, mx), mn)

    # remove non-letters, links and "rt" notation from tweets
    @staticmethod
    def cleanText(s):
        # remove rt notation and links
        s = str(s).replace('rt ', '')
        s = re.sub(r'https?:\/\/\S+', '', s)
        s = re.sub(r'@\w{1,15}(?!\w)', '', s)
        # remove non-letters
        s = re.sub(r'[^\'a-zA-Z\s]', '', s)
        return s
