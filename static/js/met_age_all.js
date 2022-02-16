import {initialise_met_table, updateMetboliteSidePanel, updatePathwayPanel, updateGenePanel} from './metabolite_tables_general.js';

$(document).ready(function() {

  $("fieldset[class^='peak_details']").hide();
  $("#pathwaysDiv").hide();
  $("#geneDiv").hide();


  let peak_url = `peak_age_explorer/`
  let pathway_url = `pathway_age_search`
  let gene_url =`gene_age_explorer`
  let metabolite_table = initialise_met_table("metabolite_list");

  console.log("pre_pwy_url", pathway_url)
      metabolite_table.on( 'click', 'tr', function () {
      updateMetboliteSidePanel(this, peak_url);
      updatePathwayPanel(this, pathway_url);
      updateGenePanel(this, gene_url);
      } );

});
