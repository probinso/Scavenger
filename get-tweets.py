#!/usr/bin/env python3

# Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from datetime import datetime
from pprint import pprint
from functools import partial
import json
import os
import os.path as osp
import urllib.request
import sys
import hashlib
import shutil


# loads Twitter credentials from .twitter file that is in the same directory as this script
file_dir = os.path.dirname(osp.realpath(__file__))
with open(osp.join(file_dir, '.twitter-pass')) as twitter_file:
    twitter_cred = json.load(twitter_file)

# authentication from the credentials file above
access_token        = twitter_cred["access_token"]
access_token_secret = twitter_cred["access_token_secret"]
consumer_key        = twitter_cred["consumer_key"]
consumer_secret     = twitter_cred["consumer_secret"]


def sign_path(filename, SIGTYPE=hashlib.md5):
    """
    input  :: filename and accumulating signature
    output :: unique identifier for set of filename
    """
    with open(filename, mode='rb') as f:
        d = SIGTYPE()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()


class StdOutListener(StreamListener):
    """ A listener handles tweets that are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def __init__(self, filename):
        self.filename = filename

    # this is the event handler for new data
    def on_data(self, data):
        print("*", end='', file=sys.stderr)
        tweet    = json.loads(data)

        username = tweet['user']['name']
        media    = tweet['extended_entities'].get('media', [])
        for entry in media:
            print(username, end=' : ', file=sys.stderr)
            print(entry['type'], end=' : ', file=sys.stderr)


            post_type = entry['type']
            if post_type == 'photo':
                url = entry['media_url']
            elif post_type == 'video':
                print(entry['video_info'], file=sys.stderr)
                urls = entry['video_info']['variants']
                url = next(filter(lambda x: x.get('content_type', '').find('video/') == 0, urls))['url']

            print(url, file=sys.stderr)
            _, ext = url.rsplit('.', 1)

            filename, headers = urllib.request.urlretrieve(url)
            new_name = sign_path(filename)
            shutil.move(filename, './'+new_name+'.'+ext)
            print(filename, file=sys.stderr)

    # this is the event handler for errors
    def on_error(self, status):
        print(status, file=sys.stderr)


user_ids = {'776268767152119808':'Team1', '776298156967342080':'Team2'}
if __name__ == '__main__':
    listener = StdOutListener(osp.join(file_dir, 'tweets.txt'))
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    print("Use CTRL + C to exit at any time.\n")
    stream = Stream(auth, listener)
    stream.filter(follow=user_ids.keys())
