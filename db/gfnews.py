import requests
import MySQLdb as mdb
import demjson
import re
import time
from datetime import datetime, date, timedelta
from summarize import extractSummary
from html import unescape
"""
Notes on googleFinance news JSONP response
-----------------------------------------------------------------------------
GoogleFinance clusters articles that have similar content. The response is
an array of nested dictionaries, each corresponding to a cluster of articles. Each
cluster identified by a lead article, and each article in that cluster is closely
related to said lead article.

The strutcure of these clusters follows:
{
    ....
    "lead_story_url": str
    "a": [  ....
            {
                "s": "Motley Fool",
                "d": "Nov 23, 2016",
                "sp": "sp": "According to a report....third quarter of 2016.",
                "t": "Apple Inc.&#39;s Mysterious OLED iPhone Revealed"
                "u": "'http://www.fool.com/investing/....revealed.aspx"
            }
            ....
        ]
}
"""

db_host = '127.0.0.1'
db_user = 'sec_user'
db_pass = 'password'
db_name = 'securities_master'
db_port = 3306


def _parse_date(date_str):
    """ Turns a date string into a valid datetime object"""
    date_str_regex = re.compile("[\w]{3} [\d]{1,2}, [\d]{4}")
    hours_ago_regex = re.compile("[\d]{1,2} [\w]+ ago")

    if date_str_regex.match(date_str):
        try:
            return datetime.strptime(date_str, "%b %d, %Y")
        except ValueError:
                pass
    elif hours_ago_regex.match(date_str):
        try:
            return datetime.combine(date.today(), datetime.min.time())
        except:
            pass
    raise ValueError("couldn't parse date string: {0}".format(date_str))


def _make_keys_verbose(article_dict):
    old_to_new = {
        "a": "articles", "d": "date", "s": "source", "t": "title",
        "tt": "titleId", "u": "url", "sp": "openingSentence"
    }

    for old_key in article_dict:
        if old_key in old_to_new:
            new_key = old_to_new[old_key]
            article_dict[new_key] = article_dict.pop(old_key)


def _get_articles(symbol, num_articles=500):
    """ return tuples (date, title, summary"""
    payload = {
        "output": "json",
        "q": symbol,
        "num": num_articles,
        "start": 0
    }
    try:
        resp = requests.get("http://www.google.com/finance/company_news?",
                                params=payload)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        return
    clusters = demjson.decode(resp.text)['clusters']
    # need demjson's decode, json data is invalid for pythons native decoder
    articles = []
    for cluster in clusters:
        if "a" in cluster:
            for article in cluster["a"]:
                _make_keys_verbose(article)
                date = _parse_date(article["date"])
                src = article['source']
                title = unescape(article['title'])
                url = article['url']
                summary = extractSummary(url)
                if not summary:
                    continue
                articles.append( (date, src, url, title, summary) )
    return articles


def get_ids_and_tickers():
    """
    Retrieves list of ids and corresponding ticker for all symbols in the
    symbol table.

    Returns:
        list: [(id, ticker) for every ticker found in the database]
    """
    conn = mdb.connect(db_host, db_user, db_pass, db_name, db_port)
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT id, ticker FROM symbol')
        rows = cur.fetchall()
        return [(row[0], row[1]) for row in rows]


def insert_snp500_news():
    columns_str = "symbol_id, article_date, source, url, title, summary"
    fill_str = "%s, %s, %s, %s, %s, %s"
    template_insert_str = ("INSERT IGNORE INTO articles ({columns}) "
                           "VALUES ({vals})".format(columns=columns_str,
                                                    vals=fill_str))
    conn = mdb.connect(db_host, db_user, db_pass, db_name, db_port,
                       use_unicode=True, charset="utf8")
    cursor = conn.cursor()
    with conn:
        for id, ticker in get_ids_and_tickers():
            print("Adding news articles for {0}".format(ticker))
            articles = _get_articles(ticker, num_articles=3)
            # add the symbol_id to the rows
            articles = [ (id, *t) for t in articles ]
            cursor.executemany(template_insert_str, articles)
            conn.commit()
            time.sleep(60)
