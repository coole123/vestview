$(function () {
    /**
     * Create the stock chart when all data is loaded
     * @returns {undefined}
     */
    var seriesOptions = [], seriesCounter = 0, colorsCounter = 0;
    var tickers = window.location.href.split("/");
    tickers = tickers[tickers.length - 1];
    tickers = tickers.split("&");

    colors = ['#7cb5ec', '#434348', '#90ed7d', '#f7a35c', '#8085e9',
   '#f15c80', '#e4d354', '#2b908f', '#f45b5b', '#91e8e1']
    function createStockChart() {
        Highcharts.stockChart('stockchart', {
            rangeSelector: {
                selected: 0
            },
            title: {
                text: 'Daily Stock Price',
                x: -20
            },
            navigator: {
                    enabled: false
            },
            yAxis: [{ //primary axis -- stock prices
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
            }, { //secondary axis -- wikipedia views
                title: {
                    text: 'Weekly Wikipedia Views',
                    x: -20 //center
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            }],
            plotOptions: {
                series: {
                    compare: 'percent',
                    showInNavigator: true
                }
            },
            tooltip: {
                shared: true
            },
            legend: {
                layout: 'vertical',
                align: 'left',
                x: 80,
                verticalAlign: 'top',
                y: 55,
                floating: true,
                backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
            },
            series: seriesOptions
        });
    }

    for( var ticker in dailyPrices ){
       seriesOptions[seriesCounter] = {
            name: ticker,
            data: dailyPrices[ticker],
            color: colors[colorsCounter],
            yAxis: 0
        }
        seriesCounter += 1;
        seriesOptions[seriesCounter] = {
            name: ticker,
            data: dailyViews[ticker],
            dashStyle: "Dash",
            color: colors[colorsCounter],
            yAxis: 1
        }
        seriesCounter += 1;
        colorsCounter += 1;
    }

    createStockChart();


    $.each(tickers, function(i, ticker){
        var navid = "#nav-" + ticker;
        var accid = "#accordion-" + ticker;
        $(navid).on("click", function(){
            $(accid).show().siblings("div.accordion").hide()
        });
    });
    // all are hidden by default, so show the first tab on page open
    $("#accordion-" + tickers[0]).show();

});
