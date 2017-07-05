#!/usr/bin/env python3

# Batteries
from functools import partial
import hashlib
import json
import os
import os.path as osp
import sys
import urllib.request
import shutil

# Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy   import OAuthHandler, Stream
from datetime import datetime
from pprint   import pprint

# Local
import model


# loads Twitter credentials from .twitter file
#   that is in the same directory as this script
file_dir = os.path.dirname(osp.realpath(__file__))
with open(osp.join(file_dir, '.twitter-pass')) as \
     twitter_file:
    twitter_cred = json.load(twitter_file)

# authentication from the credentials file above
access_token        = twitter_cred['access_token']
access_token_secret = twitter_cred['access_token_secret']
consumer_key        = twitter_cred['consumer_key']
consumer_secret     = twitter_cred['consumer_secret']


def sign_path(filename, SIGTYPE=hashlib.md5):
    '''
    input  : filename and accumulating signature
    output : unique identifier for set of filename
    '''
    with open(filename, mode='rb') as f:
        d = SIGTYPE()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()


class StdOutListener(StreamListener):
    '''
    A listener handles tweets that are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    '''
    def __init__(self, filename):
        self.filename = filename

    # this is the event handler for new data
    @model.pny.db_session
    def on_data(self, data):
        print('*', end='', file=sys.stderr)

        tweet = json.loads(data)
        pprint(tweet)

        uid_str = tweet['user']['id_str']
        message = tweet['text']
        pid_str = tweet['id_str']

        U = model.User.get(id=uid_str)
        P = model.Post(id=pid_str, text=message, user=U)

        place = tweet['place']
        if place:
            geo_id = place['id']


        media = tweet.get('extended_entities', dict()).get('media', [])

        for entry in media:
            post_type = entry['type']
            if post_type == 'photo':
                url  = entry['media_url']
                Media = model.Image
            elif post_type == 'video':
                urls  = entry['video_info']['variants']
                vfilt = lambda x: x.get('content_type', '').find('video/') == 0
                url   = next(filter(vfilt, urls))['url']
                Media = model.Video
            else:
                continue
            _, ext = url.rsplit('.', 1)

            filename, headers = urllib.request.urlretrieve(url)
            new_name = sign_path(filename) + '.' + ext
            shutil.move(filename, '.' + osp.sep + new_name)
            Media(id=new_name, post=P)

    # this is the event handler for errors
    def on_error(self, status):
        print(status, file=sys.stderr)


def interface(ifname):
    with open(ifname) as fd:
        teams = json.load(fd)
    users = set()
    for T in teams:
        for U in teams[T]:
            users.add(U)

    listener = StdOutListener(osp.join(file_dir, 'tweets.txt'))
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    print('Use CTRL + C to exit at any time.\n')
    stream = Stream(auth, listener)
    stream.filter(follow=users)

if __name__ == '__main__':
    try:
        inpath  = sys.argv[1]
    except:
        print("usage: {}  <inpath>".format(
            sys.argv[0]))
        sys.exit(1)
    interface(inpath)
