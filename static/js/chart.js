$(function () {
    /**
     * Create the chart when all data is loaded
     * @returns {undefined}
     */
    function createChart() {

        Highcharts.stockChart('stockchart', {

            rangeSelector: {
                selected: 4
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

            series: series,
            title: title
        });
    }
    createChart()
});
