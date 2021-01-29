import {initialise_pals_table, updatePathwaySidePanel} from './pathway_tables_general.js';

$(document).ready(function() {
    $("fieldset[class^='pathway_details']").hide();
    $("#diagram_info").hide();

    let data_url = "pals_age_data";
    let met_ex_url = "met_age_all/"
    let pals_table = initialise_pals_table("pals_age_data", min_value, mean_value, max_value, data_url);

      pals_table.on( 'click', 'tr', function () {
        updatePathwaySidePanel(this, data_url, met_ex_url);
      } );

});
