/* This contains scripts for producing highchart tables for the FlyMet website*/

const Highcharts = require('highcharts');

require('highcharts/modules/exporting')(Highcharts);
require('highcharts/modules/data')(Highcharts);
require('highcharts/modules/drilldown')(Highcharts);
require('highcharts/highcharts-more')(Highcharts);
require('highcharts/themes/sand-signika.js')(Highcharts);

function singleMet_intensity_chart(container, series_data, drilldown_data){

  // Create the chart
  Highcharts.chart(container, {
    chart: {
      type: 'column'
    },
    title: {
      text: 'Intensity Comparison'
    },
    exporting: {
      enabled: 'averageExport',
    },
    subtitle: {
      text: 'Click the columns to view individual samples'
    },

    xAxis: [{
      id: 0,
      categories:['Female', 'Male', 'Larvae'], //Static x-axis required for error bars.

    }, {
      id: 1,
      type: 'category', //reads from the name of the drilldown/samples
    }],

    yAxis: [{
      title: {
        text: 'Relative abundance'
      },
      labels: {
        formatter: function() {
          return this.value.toExponential();
        },
      },
    }],

    legend: {
      enabled: false
    },
    plotOptions: {
      series: {
        borderWidth: 0,
      }
    },

    tooltip: {
      headerFormat: '<span style="font-size: 10px">{point.key}</span><br/>',
      pointFormat: '<span style="color:{point.color}"></span>Intensity: <b>{point.y}</b>'
    },

    series: series_data,
  // [[ 654127655, 641653789, 621125456] [745231112, 723223855, 1100098987], [1120993441, 850003341, 1384887665], [ 45000456, 670881112, 512986512]]

  drilldown: {

    series: drilldown_data
  },
});

}

export {singleMet_intensity_chart}
