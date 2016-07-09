#!/usr/bin/env python3

# Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from datetime import datetime
from pprint import pprint
import json
import os
import os.path as osp

# loads Twitter credentials from .twitter file that is in the same directory as this script
file_dir = os.path.dirname(osp.realpath(__file__)) 
with open(osp.join(file_dir, '.twitter-pass')) as twitter_file:  
    twitter_cred = json.load(twitter_file)

# authentication from the credentials file above
access_token        = twitter_cred["access_token"]
access_token_secret = twitter_cred["access_token_secret"]
consumer_key        = twitter_cred["consumer_key"]
consumer_secret     = twitter_cred["consumer_secret"]


class StdOutListener(StreamListener):
    """ A listener handles tweets that are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def __init__(self, filename):
        self.filename = filename

    # this is the event handler for new data
    def on_data(self, data):
        data  = json.loads(data)
        media = data['entities'].get('media', [])
        if media:
            print("NEW ENTRY")
        for entry in media:
            print(entry['type'], entry['media_url'])
        

    # this is the event handler for errors    
    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    listener = StdOutListener(osp.join(file_dir, 'tweets.txt'))
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    print("Use CTRL + C to exit at any time.\n")
    stream = Stream(auth, listener)
    stream.filter(track=['slut'], async=True)
