from flask import Flask, render_template, jsonify
from datetime import datetime
import requests
import json
import sys
import MySQLdb as mdb

app = Flask(__name__)

def get_quotes(symbols):
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


def get_autocomplete_data():
    conn  = mdb.connect('127.0.0.1', 'sec_user', 'password', 'securities_master')
    cursor = conn.cursor()
    cursor.execute('SELECT ticker, name FROM symbol')
    all_tickers = [ ticker for ticker, _ in cursor ]
    company_names = { ticker:name for ticker, name in cursor }
    quotes = get_quotes(all_tickers)
    return [ {'label':company_names[d['symbol']], 'value':d['symbol'],
              'price':float(d['LastTradePriceOnly'])} for d in quotes ]


@app.route('/')
def root():
    """
    This will serve the homepage template
    The data JSON obj is sent to the client side for real-time
    autocomplete data
    """
    data = get_autocomplete_data()
    return render_template("search.html", autocompleteData=data)


def get_wiki_views_series(symbol):
    conn  = mdb.connect('127.0.0.1', 'sec_user', 'password', 'securities_master')
    cursor = conn.cursor()
    cursor.execute(('SELECT dv.views_date, dv.views '
                    'FROM symbol AS sym '
                    'INNER JOIN '
                    'daily_wiki_views AS dv '
                    'ON sym.id = dv.symbol_id '
                    'WHERE sym.ticker="{0}" '
                    'ORDER BY dv.views_date ASC').format(symbol))

    views = [ [date.timestamp() * 1000, int(views)] for date, views in cursor if views]
    return views

def get_daily_price_series(symbol):
    conn  = mdb.connect('127.0.0.1', 'sec_user', 'password', 'securities_master')
    cursor = conn.cursor()
    cursor.execute(('SELECT dp.price_date, dp.adj_close_price '
                    'FROM symbol AS sym '
                    'INNER JOIN '
                    'daily_price AS dp '
                    'ON sym.id = dp.symbol_id '
                    'WHERE sym.ticker="{0}" '
                    'ORDER BY dp.price_date ASC').format(symbol))
    prices = [ [date.timestamp() * 1000, float(price)] for date, price in cursor if price]
    return prices

@app.route("/chart/<symbol>")
def graph(symbol):
    """
    This function essentialy serves the page for http://vestview.com/stock/<SYMBOL>
    TODO: Add multiple stock functionality, make graph more interactive, and update
    graph.html template
    """
    views = get_wiki_views_series(symbol)
    prices = get_daily_price_series(symbol)
    print(views[:10])
    print("--------------------------------")
    print(prices[:10])
    return render_template('chart.html', prices=prices, views=views)



    price_series = [ {date.timestamp() * 1000: float(price)} for date, price in cursor if price]
    return price_series

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
