//This is the JavaScript that is required for the metabolite_search page.
require('./init_datatables')
require('bootstrap/js/dist/tooltip');

Awesomplete = require('awesomplete');
require('awesomplete/awesomplete.css');
require('../css/awesomechanges.css')

import {initialise_table, updateMetSidePanel} from './flymet_tables';
// import {singleMet_intensity_chart} from './flymet_highcharts.js';
// import {test_chart} from './flymet_highcharts.js';

//Update the metabolite side panel depending on which row is selected.
//Let tissue name = the first text sent back from the row (more or less)
// function updateMetSidePanel(obj, metabolite){
//   let tissue_name = $(obj).children().first().text();
//
//   console.log(tissue_name)
//
//   const series_data = [ { xAxis: 0, name: "Life Stages", id: "master_1", data: null},
//   { name: 'IQR',
//   type: 'errorbar',
//   linkedTo: "master_1",
//   data: null,
//   marker: {
//     enabled: false
//   },
//   pointWidth: 15, // Sets the width of the error bar -- Must be added, otherwise the width will change unexpectedly #8558
//   pointRange: 0,  //Prevents error bar from adding extra padding on the X-axis
//   tooltip: {
//     pointFormat: ''
//   }
//   //stemWidth: 10,
//   //whiskerLength: 5
// }
// ];
//
// const drilldown_data = [
//   {
//     xAxis: 1,
//     name: "F",
//     id: "1",
//     data: null
//   },
//   {
//     xAxis: 1,
//     name: "FW",
//     id: "2",
//     data: null
//   },
//   {
//     xAxis: 1,
//     name: "M",
//     id: "3",
//     data: null
//   },
//   {
//     xAxis: 1,
//     name: "MW",
//     id: "4",
//     data: null
//   },
//   {
//     xAxis: 1,
//     name: "L",
//     id: "5",
//     data: null
//   },
//   {
//     xAxis: 1,
//     name: "LW",
//     id: "6",
//     data: null
//   },
//
// ];
//
// const handleUpdate = function(returned_data) {
//
//   const probability = returned_data.probability;
//
//   series_data[0].data = returned_data.series_data;
//   series_data[1].data = returned_data.error_bar_data;
//
//   // Fill in the drill down data for each lifestage.
//   const returned_drill =  returned_data.drilldown_data;
//   var i;
//   for (i = 0; i < returned_drill.length; i++) {
//     drilldown_data[i].data = returned_data.drilldown_data[i];
//   }
//
//   // Send on to highchart function
//   singleMet_intensity_chart('highchart', series_data, drilldown_data);
//   // Add tooltips to the highchart
//   add_highchart_tooltips(probability);
// };
//
//
//
// //const url = 'http://127.0.0.1:8000/met_explore/met_search_highchart_data/'+ tissue_name+'/'+ metabolite;
// const url = `/met_explore/met_search_highchart_data/${analysis_id}/${tissue_name}/${metabolite}`
// fetch(url)
// .then(res => res.json())//response type
// .then(handleUpdate);
//
// // find all the paragraphs with id peak in the side panel
// $("fieldset[id='click_info']").hide();
// $("fieldset[class^='peak_details']").show();
// $("p[id^='tissue_type']").text('Intensities in ' + tissue_name);
//
// // Add table header tooltips --these are temporary.
// //KMCL: These tool tips have to be replaced with something responsive - i.e. where the buttons change depending on the data.
// function add_highchart_tooltips(probability){
//   $('#I').tooltip({title: "MS peak has been Identified as " + metabolite + " using a library standard", placement: "top"});
//   $('#F').tooltip({title: "MS/MS Fragmentation data suggests that a peak is "+ probability + "% likely to be "+ metabolite, placement: "top"});
//   $('#A').tooltip({title: "This peak, annotated as Histidine, also annotates 15 other compounds", placement: "top"});
// };
//
// }

function add_table_tooltips(obj){
  $('.notDetected').tooltip({title: "A MS peak was not detected for this tissue/life stage combination", placement: "top"})
  $('.notMeasured').tooltip({title: "A sample has not been measured for this tissue/life stage combination", placement: "top"})

}

function add_met_tooltips(obj, metabolite){

  $('.AM_met_WT_ratio').tooltip({title: "Fold Change of " + metabolite + " intensity in Adult Female: Whole (7 day old) Fly vs Aged Flies", placement: "top"});
  $('.AF_met_WT_ratio').tooltip({title: "Fold change of " + metabolite + " intensity in Adult Male: Whole (7 day old) Fly vs Aged Flies", placement: "top"});
  $('.L_met_WT_ratio').tooltip({title: "Fold change of " + metabolite + " intensity in Larvae: Whole (7 day old) Fly vs Aged Flies", placement: "top"});

}

async function loadData(viewUrl) {
  try {
    const result = await $.getJSON(viewUrl);
    return result;
  } catch (e) {
    console.log(e);
  }
}

$(document).ready(function() {

  //Method to add an autocomplete search function to the DB
  loadData((url)).then(function(data) {
    new Awesomplete(metabolite_search_age, {list: data.metaboliteNames});
  });

  $("fieldset[class^='peak_details']").hide();

  console.log(pathways)
  console.log(analysis_id)

  //Wait for the table to exist before we try to use it Try/Catch block.

  try {
    let met_table = initialise_table("tissue_met_table", min, mid, max);
    add_met_tooltips(met_table);
    add_table_tooltips(tissue_met_table);

    met_table.on( 'click', 'tr', function () {
      updateMetSidePanel(this, metabolite);
    } )
  }
  catch(e) {

    if (e instanceof ReferenceError) {
    // Handle error as necessary
    console.log("waiting on table, caught", e);
    }
  }
});