from flask import Flask, render_template, jsonify
from datetime import datetime
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
    return [ {'name':company_names[d['symbol']], 'ticker':d['symbol'],
              'price':float(d['LastTradePriceOnly'])} for d in quotes ]

@app.route('/')
def root():
    """
    This will serve the homepage template
    The data JSON obj is sent to the client side for real-time
    autocomplete data
    """
    data = []
    return render_template("search.html", autocompleteData=data)

@app.route("/chart/<symbol>")
def graph(symbol):
    """
    This function essentialy serves the page for http://vestview.com/stock/<SYMBOL>
    TODO: Add multiple stock functionality, make graph more interactive, and update
    graph.html template
    """

    return render_template('chart.html', series=[], title={"text": symbol})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
