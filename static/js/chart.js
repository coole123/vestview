$(function () {
    /**
     * Create the chart when all data is loaded
     * @returns {undefined}
     */
    function createChart() {

        Highcharts.stockChart('stockchart', {

            rangeSelector: {
                selected: 1
            },

            series: [{
                name: 'AAPL',
                data: dailyPrices,
                tooltip: {
                    valueDecimals: 2
                }
            }]
        });
    }
    createChart()
});
