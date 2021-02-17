import {initialise_met_table, updateMetboliteSidePanel} from './metabolite_tables_general.js';

$(document).ready(function() {

  $("fieldset[class^='peak_details']").hide();

  let peak_url = `peak_age_explorer/`
  let metabolite_table = initialise_met_table("metabolite_list");

      metabolite_table.on( 'click', 'tr', function () {
      updateMetboliteSidePanel(this, peak_url);
      } );

});
