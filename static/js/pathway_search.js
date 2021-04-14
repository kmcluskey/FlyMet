import {enableTooltips, updatePathwayInfo, updateReactomePathway} from './pathways_general.js';
import {initialise_pwy_table} from './pathway_tables_general.js';

Awesomplete = require('awesomplete');
require('awesomplete/awesomplete.css');
require('../css/awesomechanges.css')
require('bootstrap/js/dist/tooltip');
require ('./init_datatables')

  function add_table_tooltips(obj){
    $('.notMeasured').tooltip({title: "A sample has not been measured for this tissue/life stage combination", placement: "top"})

    // age
    // $('.notMeasured').tooltip({title: "A sample has not been measured for this age/life stage combination", placement: "top"})

  }

  function add_pwy_tooltips(obj, pathway_name){

    $('#AF-pvalue').tooltip({title: "P-value of changes in the metabolites of " + pathway_name + " between female tissue & female whole Flies", placement: "top"});
    $('#AM-pvalue').tooltip({title: "P-value of changes in the metabolites of " + pathway_name + " between male tissues & male whole Flies", placement: "top"});
    $('#L-pvalue').tooltip({title: "P-value of changes in the metabolites of " + pathway_name+ " between larvae tissue & whole larvae", placement: "top"});

    // age
    // $('#AF-pvalue').tooltip({title: "P-value of changes in the metabolites of " + pathway_name + " between female aged & female whole (7 day old) flies", placement: "top"});
    // $('#AM-pvalue').tooltip({title: "P-value of changes in the metabolites of " + pathway_name + " between male aged & male whole (7 day old) flies", placement: "top"});

  }

function updatePathwayDetails(obj, met_ex_url) {

  const handleUpdate = function(returned_data) {
    updatePathwayInfo(returned_data, pathway_name, met_ex_url)
    updateReactomePathway(pathway_id, pathway_name, reactome_token)
    $("[class^='pathway_details']").show();

};
  //Update the bottom panel with a diagram using the Reactome ID.
  console.log("Pathway ID ", pathway_id)
  const url = `/met_explore/metabolite_pathway_data/${analysis_id}/${pathway_id}`
  fetch(url)
  .then(res => res.json())//response type
  .then(handleUpdate);


  $("p[id^='pwy_id']").html(`<a href="pathway_metabolites?pathway_metabolites=${pathway_name}" data-toggle="tooltip"
  title="FlyMet metabolites and peaks found in ${pathway_name}" target="_blank">${pathway_name} in FlyMet</a>`);

  enableTooltips();

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
  $("[class^='pathway_details']").hide();
  $("#diagram_info").hide();

  let met_ex_url = `met_ex_all`;
  let project = `Tissue`;
  let input = pathway_search;

  // age
  // let met_ex_url = `met_age_all`;
  // let project = `Age`;
  // let input = pathway_age_search;

  //Method to add an autocomplete search function to the DB
  loadData((url)).then(function(data) {
    new Awesomplete(pathway_search, {list: data.pathwayNames});
  });
  // If the pathway_id has been returned from tne page
  if (pathway_id) {
    try {
      let pwy_table = initialise_pwy_table('pwy_table', pals_min, pals_mid, pals_max, project);
      add_table_tooltips(pwy_table);
      add_pwy_tooltips(pwy_table, pathway_name)
      updatePathwayDetails(this, met_ex_url);

  }
  catch(e) {
  //
    if (e instanceof ReferenceError) {
  //   // Handle error as necessary
   console.log("waiting on pathway to be passed, caught", e);
    }
  }
}
  console.log('pathway passed', pathway_name);
  console.log('url', url)

});
