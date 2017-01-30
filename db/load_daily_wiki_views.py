import requests
import datetime
import MySQLdb as mdb
from mwviews.api import PageviewsClient

db_host = '127.0.0.1'
db_user = 'sec_user'
db_pass = 'password'
db_name = 'securities_master'
db_port = 3306
conn = mdb.connect(db_host, db_user, db_pass, db_name, db_port)

def get_symbol_ids_and_wiki_titles():
    """
    Retrieves list for all symbol ids and their respective wikipedia page title
    for every symbol in the symbol table.

    Returns:
        list: [(id, wiki_title) for every ticker found in the database]
    """
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT id, wiki_title FROM symbol')
        rows = cur.fetchall()
        return [(row[0], row[1]) for row in rows]

def get_snp500_wiki_views(start=None, end=None):
    """
    Inserts wiki page views into the daily_views table

    Parameters:

        start (str, datetime): YYYYMMDD
        end   (str, datetime): YYYYMMDD
    """
    pvc = PageviewsClient()
    symbol_ids_and_titles = get_symbol_ids_and_wiki_titles()
    title_to_id = { title:id for id, title in symbol_ids_and_titles }
    articles = [ title for _, title in symbol_ids_and_titles ]
    project = 'en.wikipedia'
    now = datetime.datetime.utcnow()

    # API call
    views_dict = pvc.article_views(project, articles, start=start, end=end)
    # transforming API call to rows (a list of tuples)
    daily_views = []
    for date in views_dict:
        for title in views_dict[date]:
            id, views = title_to_id[title], views_dict[date][title]
            daily_views.append((id, date, views, now, now))

    return daily_views


def insert_snp500_wiki_views(start=None, end=None):
    daily_views = get_snp500_wiki_views(start, end)
    columns_str = ("symbol_id, views_date, views, created_date, last_updated_date")
    fill_str = "%s, %s, %s, %s, %s"
    template_insert_str = ("INSERT INTO daily_wiki_views ({columns})"
                          "VALUES ({vals})".format(columns=columns_str,
                                                   vals=fill_str))
    with conn:
        cur = conn.cursor()
        cur.executemany(template_insert_str, daily_views)


if __name__ == "__main__":
    insert_snp500_wiki_views(start='20150101')
