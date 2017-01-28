import datetime
import MySQLdb as mdb
import requests
# ignore truncation warnings
from warnings import filterwarnings

filterwarnings('ignore', category=mdb.Warning)
db_host = '127.0.0.1'
db_user = 'sec_user'
db_pass = 'password'
db_name = 'securities_master'
db_port = 3306
conn = mdb.connect(db_host, db_user, db_pass, db_name, db_port)

def get_tickers():
    """
    Retrieves list for all symbols in the symbol table.

    Returns:
        list: [(id, ticker) for every ticker found in the database]
    """
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT id, ticker FROM symbol')
        rows = cur.fetchall()
        return [(row[0], row[1]) for row in rows]

def get_daily_yahoo_historical(ticker, start=(2000, 1, 1),
                         end=datetime.date.today().timetuple()[0:3]):
    """
    Retrieve daily hisotircal OHLC data from Yahoo Finance API

    Parameters:
        ticker (str)  : Ticker you want historical data for
        start  (tuple): (YYYY, MM, DD)
        end    (tuple): (YYYY, MM, DD)

    Returns:
        List[tuple]:
            [ (Date, Open, High, Low, Close, Volume, AdjClose) ...]
    """
    YFINANCE_CSV_URL = ('http://ichart.finance.yahoo.com/table.csv?'
                       's=%s&a=%s&b=%s&c=%s&d=%s&e=%s&f=%s')
    req_url = YFINANCE_CSV_URL % (ticker, start[1]-1, start[2], start[0],
                                  end[1]-1, end[2], end[0])
    try:
        resp = requests.get(req_url)
        resp.raise_for_status()

        yahoo_data_iter = iter(resp.iter_lines())
        next(yahoo_data_iter) # ignore header
        daily_prices = []

        for day in yahoo_data_iter:
            row = day.decode('utf-8').split(',')
            daily_prices.append( (datetime.datetime.strptime(row[0], '%Y-%m-%d'),
                                  row[1], row[2], row[3], row[4], row[5], row[6]))
    except requests.exceptions.RequestException as e:
        print(e)
        return

    return daily_prices

def insert_daily_historical_db(data_vendor_id, symbol_id, daily_data):
    now = datetime.datetime.utcnow()
    """
    Inserts all the daily hisorical data into the daily_price table.

    Parameters:
        date_vendor_id (int) : Id to uniquely identify the vendor of stock data
        symbol_id (int) : Id of the stock (foreign key to symbol table)
        daily_data (list) : The rows of data returned from `get_daily_yahoo_historical`
    """

    # add data vendor and symbol id to data
    daily_prices = [(data_vendor_id, symbol_id, t[0], now, now, *t[1:]) for t in daily_data]
    columns = ("data_vendor_id, symbol_id, price_date, created_date, last_updated_date,"
               "open_price, high_price, low_price, close_price, volume, adj_close_price")
    fill_str = ("%s, " * 11)[:-2]
    template_insert_str = ("INSERT INTO daily_price ({columns}) "
                          "VALUES ({vals})".format(columns=columns, vals=fill_str))
    chunks = [daily_prices[i:i+100] for i in range(0, len(daily_prices), 100)]
    with conn:
        cur = conn.cursor()
        for chunk in chunks:
            cur.executemany(template_insert_str, chunk)

if __name__ == "__main__":
    # Loop over the tickers and insert the daily historical
    # data into the database
    tickers = get_tickers()
    for id, ticker in tickers:
        print("Adding data for {0}".format(ticker))
        data = get_daily_yahoo_historical(ticker, start=(2014,1 ,1))
        insert_daily_historical_db('1', id, data)
