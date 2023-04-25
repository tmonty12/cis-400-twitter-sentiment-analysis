from flask import render_template, flash
from src import app
from src.forms import SearchUserForm
from src.api import Twitter
from src.analysis import SentimentAnalysis

sentiment_score_color = {
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

sentiment_score_description = "Measures the sentiment of tweets the user is mentioned in to display an overall score on other's perception of the target user."
topics_description = 'Top topics in tweets mentioning user'

twitter = Twitter('AAAAAAAAAAAAAAAAAAAAAP1GlQEAAAAAr4QwhuBnlJtvQBM5%2FpnXgbCFmtI%3D69hujxQ40RCsLqV9Qz8abUVXDIKvgfwweM8YLfhj1NRBfaVDe8')
s = SentimentAnalysis()

elon = {
    'sentiment_score': 2,
    'topics': ['Tesla', 'Twitter', 'Spacex', 'Mars', 'Memes']
}

rock = {
    'sentiment_score': 8,
    'topics': ['Teramana', 'Zoa', 'XFL', 'Under Armour', 'Jumanji']
}

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
            tweets = twitter.get_mentions_pagination(user_id, 1000)
            num_tweets = len(tweets)
            s.load_tweets(tweets, username)
            top5words = s.top5words()
            top5usernames = s.top5usernames()
            sentiment_score = round(9 * s.reputation_score() + 1, 0)

    return render_template('index.html', form=form, username=username, sentiment_score=sentiment_score, sentiment_color=sentiment_score_color[sentiment_score], sentiment_score_description=sentiment_score_description, topics=top5words, usernames=top5usernames, topics_description=topics_description, num_tweets=num_tweets)