from flask import render_template, flash
from src import app
from src.forms import SearchUserForm

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
    obj = {
        'sentiment_score': 1,
        'topics': []
    }

    if form.validate_on_submit():

        # Case where username does not exist
        # Currently all usernames that aren't elon dne
        if form.username.data != 'elon' and form.username.data != 'rock' :
            flash(f'Sorry but the user {form.username.data} does not exist. Please try a different user.')
            username = None
        else:
            username = form.username.data
            if username == 'elon':
                obj = elon
            else:
                obj = rock
            


    return render_template('index.html', form=form, username=username, sentiment_score=obj['sentiment_score'], sentiment_color=sentiment_score_color[obj['sentiment_score']], sentiment_score_description=sentiment_score_description, topics=obj['topics'], topics_description=topics_description)