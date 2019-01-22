/* This contains scripts for producing highchart tables for the FlyMet website*/

const Highcharts = require('highcharts');

require('highcharts/modules/exporting')(Highcharts);
require('highcharts/modules/data')(Highcharts);
require('highcharts/modules/drilldown')(Highcharts);
require('highcharts/highcharts-more')(Highcharts);
require('highcharts/themes/sand-signika.js')(Highcharts);

function singleMet_intensity_chart(container){

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
      categories:['Whole', 'Male', 'Female', 'Larvae'], //Static x-axis required for error bars.

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

    series: [ {
      xAxis: 0,
      name: "Life Stages",
      id: "master_1",
      data: [
        {
          name: "Whole Fly",
          y: 639077840,
          drilldown: "0"
        },
        {
          name: "Adult Male",
          y: 856364306,
          drilldown: "1"
        },
        {
          name: "Adult Female",
          y: 1118386000,
          drilldown: "2"
        },
        {
          name: "Larvae",
          y: 409009818,
          drilldown: "3"
        }
      ]
    },
    {

      name: 'Standard Deviation',
      type: 'errorbar',
      linkedTo: "master_1",


      data:[[621125456, 654127655],[723223855, 1100098987],[850003341, 1384887665],[45000456, 670881112]],

      marker: {
        enabled: false
      },
      pointWidth: 15, // Sets the width of the error bar -- Must be added, otherwise the width will change unexpectedly #8558
      pointRange: 0,  //Prevents error bar from adding extra padding on the X-axis
      tooltip: {
        pointFormat: ''
      }
      //stemWidth: 10,
      //whiskerLength: 5
    }
  ],
  // [[ 654127655, 641653789, 621125456] [745231112, 723223855, 1100098987], [1120993441, 850003341, 1384887665], [ 45000456, 670881112, 512986512]]

  drilldown: {

    series: [
      {
        xAxis: 1,
        name: "WF",
        id: "0",
        data: [
          [
            "WF_T1",
            654127655
          ],
          [
            "WF_T2",
            641653789
          ],
          [
            "WF_T3",
            621125456

          ],

        ]
      },
      {
        xAxis: 1,
        name: "AM",
        id: "1",
        data: [
          [
            "AM_T1",
            745231112
          ],
          [
            "AM_T2",
            723223855
          ],
          [
            "AM_T3",
            1100098987
          ],

        ]
      },
      {
        xAxis: 1,
        name: "AF",
        id: "2",
        data: [
          [
            "AF_T1",
            1120993441
          ],
          [
            "AF_T2",
            850003341
          ],
          [
            "AF_T3",
            1384887665
          ],

        ]
      },
      {
        xAxis: 1,
        name: "L",
        id: "3",
        data: [
          [
            "L_T1",
            45000456
          ],
          [
            "L_T2",
            670881112
          ],
          [
            "L_T3",
            512986512
          ],

        ]
      }

    ]
  },
});

}

export {singleMet_intensity_chart}
