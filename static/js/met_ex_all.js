import {initialise_met_table, updateMetboliteSidePanel, updatePathwayPanel} from './metabolite_tables_general.js';

$(document).ready(function() {

  $("fieldset[class^='peak_details']").hide();
  $("#pathwaysDiv").hide();

  let peak_url = `peak_explorer/`
  let metabolite_table = initialise_met_table("metabolite_list");

      metabolite_table.on( 'click', 'tr', function () {
      updateMetboliteSidePanel(this, peak_url);
      updatePathwayPanel(this);
      } );

});
