import {initialise_gene_table, updateGeneSidePanel} from './gene_tables_general.js'

$(document).ready(function() {

  $("fieldset[class^='multi_omics_details']").hide();
  let gene_table = initialise_gene_table("gene_list");
  let cmpd_url = "met_age_all"
  let pwy_url = "pathway_age_search"
  let category ="aged flies"

    gene_table.on( 'click', 'tr', function () {
      updateGeneSidePanel(this, category, cmpd_url, pwy_url);
    } );

});
