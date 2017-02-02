$(function () {
    /**
     * Create the chart when all data is loaded
     * @returns {undefined}
     */
    function createChart() {
        console.log(dailyPrices);
        Highcharts.stockChart('stockchart', {

            rangeSelector: {
                selected: 1
            },

            yAxis: [{
                labels:{
                    formatter: function() {
                        return (this.value > 0 ? '+' : '') + this.value + '%';
                    }
                }
            }],
            series: [{
                name: 'AAPL',
                data: dailyPrices,
                yAxis: 0,
                tooltip: {
                    valueDecimals: 2
                }
            }]
        });


    }
    createChart()
});
