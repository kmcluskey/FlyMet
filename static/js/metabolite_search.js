//This is the JavaScript that is required for the metabolite_search page.
require('./init_datatables')
require('bootstrap/js/dist/tooltip');

Awesomplete = require('awesomplete');
require('awesomplete/awesomplete.css');
require('../css/awesomechanges.css')

import {initialise_table} from './flymet_tables';
import {singleMet_intensity_chart} from './flymet_highcharts.js';
import {test_chart} from './flymet_highcharts.js';

//Update the metabolite side panel depending on which row is selected.
//Let tissue name = the first text sent back from the row (more or less)
function updateMetSidePanel(obj, metabolite){
    let tissue_name = $(obj).children().first().text();

    console.log(tissue_name)

    const series_data = [ { xAxis: 0, name: "Life Stages", id: "master_1", data: null},
    { name: 'IQR',
      type: 'errorbar',
      linkedTo: "master_1",
      data: null,
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
   ];

   const drilldown_data = [
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

   ];


   const handleUpdate = function(returned_data) {
     console.log(returned_data);
     series_data[1].data = returned_data.error_bar_data
     series_data[0].data = returned_data.series_data
     console.log(series_data);
     singleMet_intensity_chart('highchart', series_data, drilldown_data);
   };

   // const url = 'http://127.0.0.1:8000/met_explore/met_search_highchart_data/'+ tissue_name+'/'+ metabolite;
   const url = `http://127.0.0.1:8000/met_explore/met_search_highchart_data/${tissue_name}/${metabolite}`;
    fetch(url)
    .then(res => res.json())//response type
    .then(handleUpdate); //log the data;



    // find all the paragraphs with id peak in the side panel

    $("fieldset[id='click_info']").hide();
    $("fieldset[class^='peak_details']").show();
    $("p[id^='tissue_type']").text('Intensities in ' + tissue_name);




    // Add table header tooltips --these are temporary.
    //KMCL: These tool tips have to be replaced with something responsive - i.e. where the buttons change depending on the data.

    $('#I').tooltip({title: "MS peak has been Identified as Histidine using a library standard", placement: "top"});
    $('#I2').tooltip({title: "MS peak has been Identified as Histidine using a library standard", placement: "top"});
    $('#F').tooltip({title: "MS/MS Fragmentation data suggests that a peak is 96.2% likely to be Histidine", placement: "top"});
    $('#F1').tooltip({title: "MS/MS Fragmentation data suggests that a peak is 99% likely to be Histidine", placement: "top"});
    $('#A').tooltip({title: "This peak, annotated as Histidine, also annotates 15 other compounds", placement: "top"});
    $('#A1').tooltip({title: "This peak, annotated as Histidine, also annotates 4 other compounds", placement: "top"});
    $('#A2').tooltip({title: "This peak, annotated as Histidine, also annotates 47 other compounds", placement: "top"});
    $('#F0').tooltip({title: "There is no fragmenetation data associated with this peak", placement: "top"});


}

function add_met_tooltips(obj, metabolite){



    $('.AM_met_WT_ratio').tooltip({title: "Fold Change of " + metabolite + " intensity in Adult Female: Whole Fly vs Tissue", placement: "top"});
    $('.AF_met_WT_ratio').tooltip({title: "Fold change of " + metabolite + " intensity in Adult Male: Whole Fly vs Tissue", placement: "top"});
    $('.L_met_WT_ratio').tooltip({title: "Fold change of " + metabolite + " intensity in Larvae: Whole Fly vs Tissue", placement: "top"});

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

    $("fieldset[class^='peak_details']").hide();

    //let tissue_name = $(obj).children().first().text();

    let met_table = initialise_table("tissue_met_table", min, mid, max);
    add_met_tooltips(met_table, metabolite);

    met_table.on( 'click', 'tr', function () {
        updateMetSidePanel(this, metabolite);
    } )

    console.log('metabolite_passed', metabolite);
    //Method to add an autocomplete search function to the DB
    loadData(('http://127.0.0.1:8000/met_explore/get_metabolite_names')).then(function(data) {
        new Awesomplete(metabolite_search, {list: data.metaboliteNames});
      });

});
