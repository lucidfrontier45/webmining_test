# -*- coding: utf-8 -*-

import sys
import urllib2
import time
import sqlite3
import feedparser
import BeautifulSoup
import re

def tounicode(data):
    f = lambda d, enc: d.decode(enc)
    codecs = ['shift_jis','utf-8','euc_jp','cp932',
              'euc_jis_2004','euc_jisx0213','iso2022_jp','iso2022_jp_1',
              'iso2022_jp_2','iso2022_jp_2004','iso2022_jp_3','iso2022_jp_ext',
              'shift_jis_2004','shift_jisx0213','utf_16','utf_16_be',
              'utf_16_le','utf_7','utf_8_sig']
    for codec in codecs:
        try: return f(data, codec)
        except: continue
    return None
    
html_tags = re.compile(r'<[/\w_]+>')

opener = urllib2.build_opener()
# User-Agentヘッダーが必要
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

q = sys.argv[1]
lang = "ja"
lr= "lang_ja"

db = sqlite3.connect(sys.argv[2])
try :
    db.execute("CREATE TABLE BLOG_DATA(title, link, summary)")
    db.execute("CREATE UNIQUE INDEX url_idx on BLOG_DATA(link)")
except sqlite3.OperationalError:
    pass

last_link = ""
for n_query in xrange(0, 1000, 100):
    
    query = "http://www.google.co.jp/search?q=%s&start=%d&hl=%s&lr=%s&tbm=blg"\
                    + "&output=rss&num=100"
    query = query % (q, n_query, lang, lr)
    print "query = ", query
    
    # 検索結果全文を取得
    dat = opener.open(query).read()

    # unicodeに変換
    dat = tounicode(dat)

    # feedparserで解析
    feed = feedparser.parse(dat)

    if len(feed.entries) == 0:
        print "############################"
        print "          END               "
        print "############################"
        break

    for e in feed.entries:

        title = html_tags.sub("", e.title)
        link = e.link
        summary = BeautifulSoup.BeautifulSoup(html_tags.sub("", e.summary),
               convertEntities=BeautifulSoup.BeautifulSoup.HTML_ENTITIES).text

        sql_cmd = "INSERT OR REPLACE INTO BLOG_DATA(title, link, summary) "\
                + "values (?, ?, ?)"
        db.execute(sql_cmd, (title, link, summary))
        db.commit()

        print title
        print link
        print ""

    print link, last_link
    if link == last_link:
        break
    last_link = link
    time.sleep(0.5)

db.close()
