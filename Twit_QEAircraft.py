#!/usr/bin/env python
import tweepy

CONSUMER_KEY = "CONSUMER_KEY"
CONSUMER_SECRET = "CONSUMER_SECRET"
ACCESS_TOKEN = "ACCESS_TOKEN"
ACCESS_TOKEN_SECRET = "ACCESS_TOKEN_SECRET"

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

search = api.search(q="Queen Elizabeth")

aircraft = ['aircraft carrier no aircraft',
            'no aircraft',
            'aircraft carrier without aircraft',
            'aircraft carrier no planes',
            'no planes',
            'without planes']

jets = ['aircraft carrier no jets',
        'no jets',
        'without jets',
        'aircraft carrier without jets']

leaking = ['is sinking',
           'is leaking']

for s in search:
    for i in aircraft:
        if i == s.text:
            screen_name = s.user.screen_name
            response = "@%s Helicopters are aircraft" % screen_name
            s = api.update_status(response, s.id)
    for i in jets:
        if i == s.text:
            screen_name = s.user.screen_name
            response = "@%s The F35 testing begins this year" % screen_name
            s = api.update_status(response, s.id)
    for i in leaking:
        if i == s.text:
            screen_name = s.user.screen_name
            response = "@%s This is what sea trials are for, issues will be fixed!" % screen_name
            s = api.update_status(response, s.id)
