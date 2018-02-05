import configparser
import tweepy

config = configparser.RawConfigParser()
config.read('config.conf')

# Grab the consumer/authorization keys from config.conf
# These keys can be found here: https://apps.twitter.com/
ckey = config.get('Twitter', 'consumer_key')
csecret = config.get('Twitter', 'consumer_secret')
atoken = config.get('Twitter', 'access_token')
asecret = config.get('Twitter', 'access_secret')

# Setup Tweep Auth
auth = tweepy.OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

# Configure the Tweepy API object
api = tweepy.API(auth, wait_on_rate_limit=True)


def get_friends_list():
    # Get the user's following list
    friends_list = []

    for friend in tweepy.Cursor(api.friends).items():
        friends_list.append(friend)

    return friends_list
