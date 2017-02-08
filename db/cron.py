#!/usr/bin/env python

import MySQLdb as mdb
# ignore truncation warnings
from datetime import datetime, timedelta
from yfdaily import insert_daily_snp500
from wikidaily import insert_daily_snp500_wiki_views


def _most_recent_entry_date(conn, table, column):
    cur = conn.cursor()
    cur.execute("SELECT max({0}) AS max_date FROM {1}".format(column, table))
    try:
        return cur.fetchall()[0][0]
    except TypeError:
        print("Couldn't find entry in {0} table under {1} column...".format(table, column))
    cur.close()


def update_daily_prices(conn):
    most_recent_dt = _most_recent_entry_date(conn, table='daily_price', column='price_date')
    most_recent_dt += timedelta(days=1)
    most_recent_date = datetime.strftime(most_recent_dt, '%Y%m%d')

    insert_daily_snp500(conn, start=most_recent_date)


def update_daily_wiki_views(conn):
    most_recent_dt = _most_recent_entry_date(conn, table='daily_wiki_views', column='views_date')
    most_recent_dt += timedelta(days=1)
    most_recent_date = datetime.strftime(most_recent_dt, '%Y%m%d')

    insert_daily_snp500_wiki_views(conn, start=most_recent_date)


if __name__ == "__main__":
    # cron job should run this code daily
    from config import db_host, db_user, db_pass, db_name, db_port
    conn = mdb.connect(db_host, db_user, db_pass, db_name, db_port)
    conn.autocommit(True)
    with conn:
        update_daily_wiki_views(conn)
        update_daily_prices(conn)
