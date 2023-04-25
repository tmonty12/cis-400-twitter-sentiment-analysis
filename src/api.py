# Will Sibble
# Professor Yu
# CIS 400
# Final Project

import requests
import json
import time

# from analysis import SentimentAnalysis

TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAP1GlQEAAAAAr4QwhuBnlJtvQBM5%2FpnXgbCFmtI%3D69hujxQ40RCsLqV9Qz8abUVXDIKvgfwweM8YLfhj1NRBfaVDe8'


# Class for storing Twitter authentication methods and making API requests.
# Uses Twitter API V2 which does not require elevated access.
class Twitter():
    def __init__(self, bearer_token, base_url=None):
        self.headers = {'Authorization': f'Bearer {bearer_token}'}
        self.base_url = base_url if base_url else 'https://api.twitter.com/2/'

    # Method for creating api calls. Uses time.sleep() to wait for rate limit to be reset.
    def api_call(self, api_url, params={}):
        r = requests.get(f'{self.base_url}{api_url}', headers=self.headers, params=params)

        if r.status_code == 429:
            reset_time = int(r.headers['x-rate-limit-reset'])
            time_remaining = reset_time - time.time() + 1
            print(
                f'Rate limit hit. Will continue processing at {time.strftime("%B %d %H:%M", time.localtime(reset_time))}.')
            time.sleep(time_remaining)

            return self.api_call(api_url, params)

        elif r.status_code != 200:
            raise requests.exceptions.HTTPError()
        else:
            return json.loads(r.text)

    # Method for retrieving the id of a given username
    def get_user_id(self, username):
        user = self.api_call(f'users/by/username/{username}')
        
        if not 'data' in user:
            raise Exception(f'User with username: {username} does not exist')
        else:
            return user['data']['id']


    def get_mentions(self, user_id, pagination_token=None, ):
        params = {'max_results': '100'}

        if pagination_token:
            params['pagination_token'] = pagination_token
        
        mentions_obj = self.api_call(f'users/{user_id}/mentions', params=params)
        
        next_token = None
        if 'next_token' in mentions_obj['meta']:
            next_token = mentions_obj['meta']['next_token']

        return (mentions_obj['data'], next_token)
    
    def get_mentions_pagination(self, user_id, max_tweets):
        calls = max_tweets // 100
        tweets = []
        pagination_token = None
        for i in range(calls):
            mentions, next_token = self.get_mentions(user_id, pagination_token=pagination_token)
            tweets.extend([tweet['text'] for tweet in mentions])
            if next_token:
                pagination_token = next_token
            else:
                break
        
        return tweets

# Main function of the module for Final Project
def main(username='therock'):
    # Create Twitter class using bearer token for making Twitter API requests
    twitter = Twitter(TWITTER_BEARER_TOKEN)

    # Get id of starting user given their username
    user_id = twitter.get_user_id(username)

    #use id to get recent mentions
    tweets = twitter.get_mentions_pagination(user_id, 1000)

    s = SentimentAnalysis()
    s.load_tweets(tweets)
    s.get_usernames()

# main()
