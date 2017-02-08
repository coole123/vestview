import MySQLdb as mdb
from db import config
from flask import Flask, render_template, jsonify
from utils import (get_autocomplete_data,
                   get_wiki_views_series,
                   get_daily_price_series,
                   get_news_articles)

app = Flask(__name__)
conn = mdb.connect(config.db_host, config.db_user, config.db_pass,
                   config.db_name, config.db_port)

@app.route('/')
def root():
    """
    This will serve the homepage template
    The data JSON obj is sent to the client side for real-time
    autocomplete data
    """
    data = get_autocomplete_data(conn)
    return render_template("search.html", autocompleteData=data)


@app.route("/chart/<tickers>")
def chart(tickers):
    """
    This function serves the page for http://vestview.com/chart/<symbols>
    """
    # temporary, remove duplicate tickeres
    tickers = set(tickers.split("&"))
    views = get_wiki_views_series(conn, tickers)
    prices = get_daily_price_series(conn, tickers)
    articles = get_news_articles(conn, tickers)

    return render_template('chart.html', prices=prices, views=views,
                            articles=articles, tickers=tickers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
