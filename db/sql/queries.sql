SELECT dv.views_date, dv.views
FROM symbol AS sym
INNER JOIN
daily_wiki_views AS dv
ON sym.id = dv.symbol_id
WHERE sym.ticker='GOOG'
ORDER BY dv.views_date ASC;

