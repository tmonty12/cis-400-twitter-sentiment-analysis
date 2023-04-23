# Will Sibble
# Professor Yu
# CIS 400
# Final Project

import requests
import json
import time

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
            r_dict = json.loads(r.text)
            # If data doesn't exist in response, account is not authorized
            # to access specific data request
            if 'data' not in r_dict:
                return []
            else:
                return r_dict['data']

    # Method for retrieving the id of a given username
    def get_user_id(self, username):
        user = self.api_call(f'users/by/username/{username}')
        if not user:
            return Exception(f'User with username: {username} does not exist')
        else:
            return user['id']


    def get_mentions(self, user_id, since_id=None):
        params = {'max_results': '100'}
        if since_id:
            params['since_id'] = since_id
        return self.api_call(f'users/{user_id}/mentions', params=params)

######################################################################################################
######################################################################################################

# Main function of the module for Final Project
def main(starting_username='kingjames'):
    # Create Twitter class using bearer token for making Twitter API requests
    twitter = Twitter(TWITTER_BEARER_TOKEN)


    # Get id of starting user given their username
    starting_user_id = twitter.get_user_id(starting_username)

    #use id to get recent mentions
    recent_mentions = twitter.get_mentions(starting_user_id)

##ALTER
    print(f"Most recent mentions for user {starting_username}:")
    for mention in recent_mentions:
        #print statement to just return tweet text
        print(f"\t{mention['text']}")

        #print statement to print tweet text, time posted, and author id paramters
        #print(f"\t{mention['text']} - {mention['created_at']}")


if __name__ == '__main__':
   main()
