#!/usr/bin/python

import time
import datetime
import tweepy
import sqlite3

try:
    from collections import namedtuple
    have_namedtuple = True
    Tweet = namedtuple("Tweet", ["id", "date", "user_id", "text"])
except:
    have_namedtuple = False

api = tweepy.API()
datetime_format = "%Y-%m-%d %H:%M:%S"
wait_sec = 0.1

tweet2tuple = lambda x:(x.id, x.created_at.strftime(datetime_format),
        x.from_user_id, x.text)

def searchWord(q, lang="ja", rpp=100, since_id=0, max_id=None, go_back=False):
    tweets = []
    for page in xrange(1, 16):
        try:
            if max_id:
                tweet = api.search(q, lang=lang, rpp=rpp, since_id=since_id,
                            max_id=max_id, page=page)
            else:
                tweet = api.search(q, lang=lang, rpp=rpp, since_id=since_id,
                            page=page)
        except:
            break
        if len(tweet) == 0:
            return tweets
        tweets.extend(tweet)
        time.sleep(wait_sec)
        print "page = ", page
    if go_back:
        next_max_id = tweets[-1].id
        print "go back, max_id = ", next_max_id
        tweets.extend(searchWord(q, lang, rpp, since_id, next_max_id, go_back))
    return tweets

def dumpTweetsToSQL(dbname, tweets):
    db = sqlite3.connect(dbname)
    try :
        db.execute("CREATE TABLE TWEET_DATA(id, date, user_id, text)")
        db.execute("CREATE UNIQUE INDEX id_idx on TWEET_DATA(id)")
    except sqlite3.OperationalError:
        pass
    tweet_array = map(tweet2tuple, tweets)
    tweet_array.sort(key=lambda x:x[1])
    for tweet in tweet_array:
        sql_cmd = "INSERT OR REPLACE INTO TWEET_DATA(id, date, user_id, text)"\
                + "VALUES (?, ?, ?, ?)"
        db.execute(sql_cmd, tweet)
    db.commit()
    db.close()

def getLastIDFromSQL(dbname):
    db = sqlite3.connect(dbname)
    sql_cmd = "SELECT id FROM TWEET_DATA ORDER BY id DESC"
    try:
        last_id = db.execute(sql_cmd).fetchone()[0]
    except:
        last_id = 0
    db.close()
    return last_id

def updateTweetDB(word, dbname, go_back=False):
    if go_back:
        last_id = 0
    else:
        last_id = getLastIDFromSQL(dbname)
    tweets = searchWord(word, since_id=last_id, go_back=go_back)
    dumpTweetsToSQL(dbname, tweets)

def readAllTweetsFromSQL(dbname):
    db = sqlite3.connect(dbname)
    sql_cmd = "SELECT * FROM TWEET_DATA ORDER BY id DESC"
    tweets = db.execute(sql_cmd).fetchall()
    if have_namedtuple:
        tweets = [Tweet(t[0], datetime.datetime.strptime(t[1],
            datetime_format), t[2], t[3]) for t in tweets]
    return tweets

#def readTweetsFromSQL(dbname, begin_date=None, end_date=None):
#    db = sqlite3.connect(dbname)
#    sql_cmd = "SELECT * FROM TWEET_DATA ORDER BY id DESC"
#    if begin_date and end_date:
#        sql_cmd += " where date >= ? and date <= ?"
#        query_vals = (
#
#    if end_date:
#        sql_cmd += " and date <= ?"
#        query_values.append(str(end_date))
#

if __name__ == "__main__":
    import sys
    word = unicode(sys.argv[1], "utf-8")
    dbname = sys.argv[2]
    go_back=False
    try:
        if sys.argv[3] == "-g":
            go_back=True
    except:
        pass
    updateTweetDB(word, dbname, go_back)
