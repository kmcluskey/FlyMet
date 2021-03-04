//This is the JavaScript that is required for the metabolite_search page.
require('./init_datatables')
require('bootstrap/js/dist/tooltip');

Awesomplete = require('awesomplete');
require('awesomplete/awesomplete.css');
require('../css/awesomechanges.css')

import {initialise_table, updateMetSidePanel} from './flymet_tables';
import {get_data_index} from './metabolite_tables_general';

function add_table_tooltips(obj){
  $('.notDetected').tooltip({title: "A MS peak was not detected for this tissue/life stage combination", placement: "top"})
  $('.notMeasured').tooltip({title: "A sample has not been measured for this tissue/life stage combination", placement: "top"})
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
  //Method to add an autocomplete search function to the DB
  loadData((url)).then(function(data) {
    new Awesomplete(metabolite_search_tissue, {list: data.metaboliteNames});
  });

  $("fieldset[class^='peak_details']").hide();

  let project = `Tissue`;
  //Wait for the table to exist before we try to use it Try/Catch block.

  try {
    let num_index = get_data_index(met_table_data)
    let met_table = initialise_table("tissue_met_table", min, mid, max, project, num_index);
    add_met_tooltips(met_table, metabolite);
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
