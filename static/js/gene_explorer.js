import {initialise_gene_table, updateGeneSidePanel} from './gene_tables_general.js'

$(document).ready(function () {

    $("fieldset[class^='multi_omics_details']").hide();
    let gene_table = initialise_gene_table("gene_list");
    let cmpd_url = `met_ex_all/${analysis_id}`;
    let pwy_url = `pathway_search/${analysis_id}`;
    let category = "{{ current_category }}";

    gene_table.on('click', 'tr', function () {
        updateGeneSidePanel(this, category, cmpd_url, pwy_url);
    });

});
