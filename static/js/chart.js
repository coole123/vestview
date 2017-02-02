$(function () {
    /**
     * Create the stock chart when all data is loaded
     * @returns {undefined}
     */
    var stockSeriesOptions = [], stockSeriesCounter = 0;
    var wikiSeriesOptions = [], wikiSeriesCounter = 0;

    function createStockChart() {
        Highcharts.stockChart('stockchart', {
            rangeSelector: {
                selected: 0
            },
            title: {
                text: 'Daily Stock Price',
                x: -20
            },
            yAxis: {
                labels: {
                    formatter: function () {
                        return (this.value > 0 ? ' + ' : '') + this.value + '%';
                    }
                },
                plotLines: [{
                    value: 0,
                    width: 2,
                    color: 'silver'
                }]
            },
            plotOptions: {
                series: {
                    compare: 'percent',
                    showInNavigator: true
                }
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },
            tooltip: {
                pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.change}%)<br/>',
                valueDecimals: 2,
                split: true
            },

            series: stockSeriesOptions
        });
    }

    function createWikiChart(){
        Highcharts.stockChart('wikichart', {
            rangeSelector: {
                selected: 0
            },
            title: {
                text: 'Weekly Wikipedia Views',
                x: -20 //center
            },
            yAxis: {
                title: {
                    text: 'Views'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },
            series: wikiSeriesOptions
        })
    }

    for( var ticker in dailyPrices ){
       stockSeriesOptions[stockSeriesCounter] = {
            name: ticker,
            data: dailyPrices[ticker]
        }
        stockSeriesCounter += 1;
    }

    for( var ticker in dailyViews ){
        wikiSeriesOptions[wikiSeriesCounter] = {
            name: ticker,
            data: dailyViews[ticker]
        }
        wikiSeriesCounter += 1;
    }

    createStockChart();
    createWikiChart();
});
