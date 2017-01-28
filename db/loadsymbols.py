import datetime
import requests
import MySQLdb as mdb
from bs4 import BeautifulSoup

def obtain_parse_wiki_snp500():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = BeautifulSoup(resp.text, 'lxml')
    table = soup.find("table", { "class" : "wikitable sortable" })
    now = datetime.datetime.utcnow()
    symbols = []
    for row in table.findAll('tr'):
        cells = row.findAll('td')
        if len(cells) == 8:
            ticker = cells[0].find(text=True)
            name = cells[1].find(text=True)
            sector = cells[3].find(text=True)
            symbols.append( (ticker, 'stock', name, sector, 'USD', now, now) )

    return symbols

def insert_snp500_symbols(symbols):
    db_host = '127.0.0.1'
    port = 3306
    db_user = 'sec_user'
    db_pass = 'password'
    db_name = 'securities_master'
    conn = mdb.connect(host=db_host, port=port, user=db_user,
                       passwd=db_pass, db=db_name)

    columns_str = ("ticker, instrument, name, sector, currency,"
                   "created_date, last_updated_date")
    fill_str = "%s, %s, %s, %s, %s, %s, %s"
    template_insert_str = ("INSERT INTO symbol ({columns})"
                          "VALUES ({vals})".format(columns=columns_str,
                                                   vals=fill_str))

    with conn:
        chunks = [ symbols[i:i+100] for i in range(0, len(symbols), 100) ]
        cur = conn.cursor()
        for chunk in chunks:
            cur.executemany(template_insert_str, chunk)
if __name__ == "__main__":
    snp500_data = obtain_parse_wiki_snp500()
    insert_snp500_symbols(snp500_data)
