import {initialise_pals_table, updatePathwaySidePanel} from './pathway_tables_general.js';

$(document).ready(function() {
    $("fieldset[class^='pathway_details']").hide();
    $("#diagram_info").hide();

    const data_url = `pals_data/${analysis_id}`;
    const met_ex_url = `met_ex_all/${analysis_id}`;
    const pwy_met_url = `pathway_metabolites/${analysis_id}`;
    const table_name = "pals_data";

    let pals_table = initialise_pals_table(table_name, min_value, mean_value, max_value, data_url);

      pals_table.on( 'click', 'tr', function () {
        updatePathwaySidePanel(this, table_name, met_ex_url, pwy_met_url);
      } );

});
