from flask import render_template, flash
from src import app
from src.forms import SearchUserForm
from src.api import Twitter
from src.analysis import SentimentAnalysis
import time

sentiment_score_colors = {
    0: '#FF0000',
    1: '#FF0000',
    2: '#FF1E00',
    3: '#FF3C00',
    4: '#FF5A00',
    5: '#FF7800',
    6: '#FFB300',
    7: '#FFE000',
    8: '#D8ED00',
    9: '#B1FF00',
    10: '#00FF00'
}


def sentiment_score_color(score):
    return sentiment_score_colors[score // 10]


sentiment_score_description = "Measures the sentiment of tweets the user is mentioned in to display an overall score on other's perception of the target user."
topics_description = 'Top topics in tweets mentioning user'

twitter = Twitter(
    'AAAAAAAAAAAAAAAAAAAAAP1GlQEAAAAAr4QwhuBnlJtvQBM5%2FpnXgbCFmtI%3D69hujxQ40RCsLqV9Qz8abUVXDIKvgfwweM8YLfhj1NRBfaVDe8')
s = SentimentAnalysis()

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchUserForm()
    username = None
    top5words = []
    top5usernames = []
    sentiment_score = 1
    num_tweets = 0

    if form.validate_on_submit():
        try:
            user_id = twitter.get_user_id(form.username.data)
        except Exception:
            user_id = None

        # Case where username does not exist
        # Currently all usernames that aren't elon dne
        if not user_id:
            flash(f'Sorry but the user {form.username.data} does not exist. Please try a different user.')
            username = None
        else:
            username = form.username.data
            t1 = time.time()
            print(f'Grabbing tweet mentions for @{username}')
            tweets = twitter.get_mentions_pagination(user_id, 1000)
            t2 = time.time()
            print(f'Grabbing tweets took {t2 - t1} seconds')
            num_tweets = len(tweets)
            print(f'Loading tweets into sentiment analzer')
            s.load_tweets(tweets, username)
            t3 = time.time()
            print(f'Loading tweets took {t3 - t2} seconds')
            print(f'Grabbing the top 5 topics of the tweets')
            top5words = s.top5words()
            t4 = time.time()
            print(f'Grabbing the top 5 topics took {t4 - t3} seconds')
            print(f'Grabbing the top 5 usernames from the tweets')
            top5usernames = s.top5usernames()
            t5 = time.time()
            print(f'Grabbing the top 5 usernames took {t5 - t4} seconds')
            print(f'Analyzing the sentiment of the tweets')
            sentiment_score = round(s.reputation_score(), 0)
            t6 = time.time()
            print(f'Analyzing the sentiment took {t6 - t5} seconds\n')

    return render_template('index.html', form=form, username=username, sentiment_score=sentiment_score,
                           sentiment_color=sentiment_score_color(sentiment_score),
                           sentiment_score_description=sentiment_score_description, topics=top5words,
                           topics_description=topics_description,
                           usernames=top5usernames,
                           num_tweets=num_tweets)
