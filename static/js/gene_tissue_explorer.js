import {initialise_gene_table, updateGeneSidePanel} from './gene_tables_general.js'

$(document).ready(function() {


    $("fieldset[class^='multi_omics_details']").hide();
    // $("#diagram_info").hide();
    //
    // let data_url = "pals_data";
    // let met_ex_url = "met_ex_all/";
    // let pwy_met_url = "pathway_metabolites";
    //
    let gene_table = initialise_gene_table("gene_list");

      gene_table.on( 'click', 'tr', function () {
        console.log("I've been clicked")
        updateGeneSidePanel(this);
      } );

});
