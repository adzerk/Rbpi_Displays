from config import config
import slackclient
import json
from sys import stderr
import datetime
from collections import Counter
import pprint
import types
def login():
    key = config['slack_key']
    sc = slackclient.SlackClient(key)
    test = sc.api_call("api.test")
    t = check(test)
    return sc

def get_users(sc):        
    list_users = sc.api_call("users.list")
    lu = check(list_users)
    users = lu['members']
    return users


def search_messages(sc, search_for):
    r = sc.api_call("search.messages", query=search_for, sort='timestamp')
    resp = check(r)
    m = resp["messages"]["matches"]
    return m

def get_week_messages(sc, channel_id, start):
    r = sc.api_call("channels.history", channel=str(channel_id), sort="timestamp", oldest=str(start), count=1000)
    resp = check(r)
    m = resp["messages"]
    return m

def check(r):
    response = json.loads(r)
    if (response['ok']==True):
        print >> stderr, "fine"
        return response
    raise ResponseError(response)


class ResponseError(Exception):
    def __init__(self, response):
        self.response = response
    def __str__(self):
        return repr(self.response)



def get_channels(sc): 
    r = sc.api_call("channels.list")
    resp = check(r)
    channels = resp['channels']
    return channels

def find_channels():
    try:
        sc = login()
        channels = get_channels(sc)
        for channel in channels:
            print channel["name"] , channel["id"]
    except ResponseError as e:
        print >> stderr, e.response

def get_trello():
    try:
        sc = login()
        now = datetime.datetime.now()
        first_day = now.replace(day=1)
        y = int(first_day.strftime('%s'))
        #num_days = now - first_day
        #month = datetime.timedelta(days=30)
        #s = y.total_seconds()
        #month = y - s
        n = get_week_messages(sc, "C04TJF62C", y)
        trell = []
        for item in n:
            print >> stderr,  item 
            if 'attachments' in item.keys():
                trell.append(item['attachments'][0])
        to_crushed = []
        for x in trell:
            if 'to list "CRUSHED!"' in x['text']:
                to_crushed.append(x)
            elif 'to list "CRUSHED!"' in x['fallback']:
                to_crushed.append(x)
        return len(to_crushed)
        #print n
    except ResponseError as e:
        print >> stderr, e.response

def get_crushed():
    try:
        sc = login()
        messages = search_messages(sc, "crushed")
        i = 1
        for m in messages:
            ts_epoch = float(m['ts'])
            ts = datetime.datetime.fromtimestamp(ts_epoch).strftime('%Y-%m-%d %H:%M:%S')
            print i , ": ",ts,  m['username'], m['text']
            i += 1
        return messages
    except ResponseError as e:
        print >> stderr, e.response

def make_leaderboard():
    try:
        sc = login()
        users = get_users(sc)
        now = datetime.datetime.now()
        y = int(now.strftime('%s'))
        week = datetime.timedelta(days=7)
        s = week.total_seconds()
        last_week = y - s
        n = get_week_messages(sc,"C02JG4GCQ", last_week)
        no_text = []
        user_messages = []
        for message in n:
            if "text" in message.keys():
                user_messages.append(message)
            else:
                no_text.append(message)
        u = []
        neither = []
        print >> stderr, user_messages
        for message in user_messages:
            if 'user' in message.keys():
                u.append(message['user'])
            else:
                neither.append(message)
        print >> stderr , ("132" , u)
        user_dict = dict(Counter(u))
        leaderboard = {}
        for key, value in user_dict.items():
            for person in users:
                if person['id'] == key:
                    name = person['real_name']
                    rname = name.split(' ')
                    fname = rname[0]
                    leaderboard[value]={'id': key, 'name': fname}
        print >> stderr , leaderboard
        return leaderboard
    except ResponseError as e:
        print >> stderr, e.response

