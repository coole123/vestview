import datetime
import MySQLdb as mdb
import requests
# ignore truncation warnings
from warnings import filterwarnings
from yfdaily import insert_daily_snp500
from wikidaily import insert_daily_snp500_wiki_views

db_host = '127.0.0.1'
db_user = 'sec_user'
db_pass = 'password'
db_name = 'securities_master'
db_port = 3306


def sync_table(table, column):
    """
    Keep all stocks consistent, find the most recent entry for each individual stock.
    Then find the min of those, and delete any row who's price_date is greater.
    """
    conn = mdb.connect(db_host, db_user, db_pass, db_name, db_port)
    cur = conn.cursor()
    sync = ('SELECT min(grp.max_grped) '
             'FROM (SELECT max({0}) AS max_grped '
                    'FROM {1} '
                    'GROUP BY symbol_id) AS grp').format(column, table)
    cur.execute(sync)
    min_date = datetime.datetime.strftime(cur.fetchall()[0][0], '%Y-%m-%d')
    delete_template = 'DELETE FROM {table} WHERE {column} > "{min_date}"'
    rows = cur.execute(delete_template.format(table=table, column=column, min_date=min_date))
    print("Query OK, {0} rows affected".format(rows))


def most_recent_entry_date(table, column):
    conn = mdb.connect(db_host, db_user, db_pass, db_name, db_port)
    cur = conn.cursor()
    cur.execute("SELECT max({0}) AS max_date FROM {1}".format(column, table))
    try:
        return datetime.datetime.strftime(cur.fetchall()[0][0], '%Y%m%d')
    except TypeError:
        print("Couldn't find entry in {0} table under {1} column...".format(table, column))


def update_daily_prices():
    sync_table(table='daily_price', column='price_date')
    most_recent_date = most_recent_entry_date(table='daily_price', column='price_date')
    insert_daily_snp500(start=most_recent_date)


def update_daily_wiki_views():
    sync_table(table='daily_wiki_views', column='views_date')
    most_recent_date = most_recent_entry_date(table='daily_wiki_views', column='views_date')
    insert_daily_snp500_wiki_views(start=most_recent_date)


if __name__ == "__main__":
    update_daily_wiki_views()
    update_daily_prices()
