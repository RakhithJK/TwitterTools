#! /usr/bin/env python

# This tool is quickly thrown together to try and show some statistics on Twitter "Threadzillas".
# It works with the assumption that there are a reasonably stable amount of users being included in thread replies
# as well as the fact that a single "target" user was included in all the threadzilla replies.

# It makes a few assumptions though:
# * It's a recent threadzilla, as the standard twitter API only goes back 7 days
# * There's a steady amount of participants, and you can pick a single individual that will likely be included in all
#   replies. This is used to collect the twitter replies.

import tweepy
import configparser
import networkx as nx
import matplotlib.pyplot as plt
from terminaltables import AsciiTable

config = configparser.RawConfigParser()
config.read('config.conf')

# Grab the consumer/authorization keys from config.conf
# These keys can be found here: https://apps.twitter.com/
ckey = config.get('Twitter', 'consumer_key')
csecret = config.get('Twitter', 'consumer_secret')
atoken = config.get('Twitter', 'access_token')
asecret = config.get('Twitter', 'access_secret')

# Get the configuration for the target user and participant count threshold
target_user = config.get('Twitter', 'target_user')
participant_count = config.getint('Twitter', 'participant_count')

# Setup Tweep Auth
auth = tweepy.OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

# Configure the Tweepy API object
api = tweepy.API(auth, wait_on_rate_limit=True)

# Collect the target user's (the one hopefully included in most of the threadzilla) reply tweets
print("Grabbing results from Twitter API...")
results = [status for status in tweepy.Cursor(api.search, q=target_user, tweet_mode='extended').items(1000)]
print("Finished getting Twitter results!")

# Logic gets a bit fuzzy here, we want to filter out any messages that aren't likely a part of the threadzilla
# participant_count is the rough number of participants in the threadzilla

# Put all the threadzilla replies into a list
threadzilla_replies = []

# Iterate through the replies and pull out any replies that reach the threshold count of participants
for reply in results:
    if len(reply.entities['user_mentions']) > participant_count:
        threadzilla_replies.append(reply)

# Build an [tweet ID, in_reply_to ID] list for graphing
id_list = []
for reply in threadzilla_replies:
    id_list.append((reply.id, reply.in_reply_to_status_id))

# Setup the Graph and add the nodes
graph = nx.Graph()
graph.add_edges_from(id_list)

# Draw the Graph
print("Drawing graph... Close the graph window to continue...")
nx.draw_spring(graph)
plt.show()

# Start to build up a thread contribution table
thread_contributors = {}

for reply in threadzilla_replies:
    if reply.author.screen_name not in thread_contributors.keys():
        thread_contributors[reply.author.screen_name] = 1
    else:
        thread_contributors[reply.author.screen_name] += 1

# Build a list of out the contributors dictionary to properly sort
clist = []

for c in thread_contributors:
    clist.append(['@' + c, thread_contributors[c]])

# Sort the list based on the number of replies, sort in descending order
# .sort() modifies the list in place
clist.sort(key=lambda x: x[1], reverse=True)

# Build a table that we're going to be printing
# I feel like I'm making too many objects for this list/table building, but meh!
table_list = [['Username', 'Message Count']]

for c in clist:
    table_list.append(c)

# Build and print the AsciiTable
table = AsciiTable(table_list)
print(table.table)

