SELECT dv.views_date, dv.views
FROM symbol AS sym
INNER JOIN
daily_wiki_views AS dv
ON sym.id = dv.symbol_id
WHERE sym.ticker='GOOG'
ORDER BY dv.views_date ASC;

SELECT dp.price_date, dp.adj_close_price
FROM symbol AS sym
INNER JOIN
daily_price  AS dp
ON sym.id = dp.symbol_id
WHERE sym.ticker='GOOG'
ORDER BY dp.price_date ASC;
