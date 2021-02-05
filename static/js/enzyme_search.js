require('./init_datatables')
require('bootstrap/js/dist/tooltip');
import {initialise_table} from './flymet_tables';
import {init_met_side_table} from './flymet_tables';
// import {add_met_tooltips} from './flymet_tables';
import {updateEnzymeSidePanel} from './flymet_tables';

// import {singleMet_intensity_chart} from './flymet_highcharts.js';
import {test_chart} from './flymet_highcharts.js';


// <!-- jQuery first, then Popper.js, then Bootstrap JS -->
// <!--replaced slim version of jquery to include ajax and the effects modules-->


// // <!-- <script src="../js/flymet_tempchart.js"></script> -->
// <script src="../js/flymet_highcharts.js"></script>
// <script src="../js/flymet_tables.js"></script>

// <!-- Initialise the table on this page-->

// <script>
// Runs once the page Document Object Model (DOM) is ready for JavaScript code to execute.
$(document).ready(function() {


  //$("fieldset[class^='reaction_details']").hide();
  $("fieldset[class^='reaction_details']").hide();
  let enzyme_table = initialise_table("gene_table",0.0,18.0, 37.0);

  $('#has_enzyme').tooltip({title: "Histidine decarboxylase is found in this reaction", placement: "top"});
  $('#has_pathway').tooltip({title: "Histidine decarboxylase is found in this pathway", placement: "top"});


  enzyme_table.on( 'click', 'tr', function () {
    updateEnzymeSidePanel(this);
  } )
  var side_table = init_met_side_table("reaction_metabolites",0.0,6.0,13.0);
  // add_met_tooltips(side_table);
});

// </script>
