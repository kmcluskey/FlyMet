import {initialise_gene_table, updateGeneSidePanel} from './gene_tables_general.js'

$(document).ready(function() {

    $("fieldset[class^='multi_omics_details']").hide();

    let cmpd_url = "met_ex_all"
    let pwy_url = "pathway_search"
    let category ="tissues"

    let gene_table = initialise_gene_table("gene_list");

      gene_table.on( 'click', 'tr', function () {
        console.log("I've been clicked")
        updateGeneSidePanel(this, category, cmpd_url, pwy_url);
      } );

});
