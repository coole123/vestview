"""
These functions are used in `app.py` to send data to the front end JavaScript
files. They either query the MySQL database for stored data, or query other APIs
for real-time data, and all of them return JSON objects.
"""

import json
import MySQLdb as mdb
import requests
from datetime import datetime


def _get_quotes(symbols):
    """
    Queries the public Yahoo Finance API for quotes.
    """
    # have to format symbols list to from ("SYM1", "SYM2", .... ,"SYMN")
    symbols = "(" + ",".join(['\"' + s.upper() + '"' for s in symbols]) + ")"
    query = 'SELECT * FROM yahoo.finance.quote WHERE symbol in {0}'.format(symbols)
    payload = {
        "q": query, 'format':'json', "env":'store://datatables.org/alltableswithkeys'
    }
    try:
        resp = requests.get('http://query.yahooapis.com/v1/public/yql?', params=payload)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        return
    return json.loads(resp.text)["query"]["results"]["quote"]


def get_autocomplete_data(conn):
    cur = conn.cursor()
    cur.execute('SELECT ticker, name FROM symbol')
    all_tickers = [ ticker for ticker, _ in cur ]
    company_names = { ticker:name for ticker, name in cur }
    quotes = _get_quotes(all_tickers)
    allData = []
    for d in quotes:
        quote = {
            'company': company_names[ d['symbol'] ],
            'ticker': d['symbol'],
            'price': float(d['LastTradePriceOnly']) if d['LastTradePriceOnly'] else None,
            'change': float(d['Change']) if d['Change'] else None
        }
        allData.append(quote)

    cur.close()
    return allData

def get_index_data():
    """
    Gets index data for marquee
    """
    all_indexes = ['^DJI', '^RUA', '^GSPC', '^IXIC', '^SZSA', '^XCI', '^MSH']


def get_wiki_views_series(conn, tickers):
    cur = conn.cursor()
    views = {}
    for ticker in tickers:
        cur.execute(('SELECT dv.views_date, dv.views '
                        'FROM symbol AS sym '
                        'INNER JOIN '
                        'daily_wiki_views AS dv '
                        'ON sym.id = dv.symbol_id '
                        'WHERE sym.ticker="{0}" '
                        'ORDER BY dv.views_date ASC').format(ticker))
        views[ticker] = [ [date.timestamp() * 1000, int(views)]
                          for date, views in cur if views ]
    cur.close()
    return views


def get_daily_price_series(conn, tickers):
    cur = conn.cursor()
    prices = {}
    for ticker in tickers:
        cur.execute(('SELECT dp.price_date, dp.adj_close_price '
                        'FROM symbol AS sym '
                        'INNER JOIN '
                        'daily_price AS dp '
                        'ON sym.id = dp.symbol_id '
                        'WHERE sym.ticker="{0}" '
                        'ORDER BY dp.price_date ASC').format(ticker))
        prices[ticker] = [ [date.timestamp() * 1000, float(price)]
                           for date, price in cur if price]
    cur.close()
    return prices


def get_news_articles(conn, tickers):
    cur = conn.cursor()
    allArticles = {}
    for ticker in tickers:
        cur.execute(('SELECT a.article_date, a.source, a.url, a.title, a.summary '
                     'FROM symbol AS sym '
                     'INNER JOIN '
                     'articles AS a '
                     'ON sym.id = a.symbol_id '
                     'WHERE sym.ticker="{0} " '
                     'ORDER BY a.article_date ASC').format(ticker))
        articles = []
        for date, src, url, title, summary in cur:
           articles.append({'date': date, 'source': src, 'url': url,
                            'title': title, 'summary': summary})
        allArticles[ticker] = articles

    cur.close()
    return allArticles
