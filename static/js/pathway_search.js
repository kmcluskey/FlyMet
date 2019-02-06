require('./init_datatables')
require('bootstrap/js/dist/tooltip');
import {initialise_table} from './flymet_tables';
import {show_hide_tables} from './flymet_tables';


$(document).ready(function() {


  //$("fieldset[class^='peak_details']").hide();

  initialise_table("pw_table_AF",-10.0, 0.0, 10);
  initialise_table("pw_table_AM",-10.0, 0.0, 10);
  initialise_table("pw_table_L",-10.0, 0.0, 10);

  $('#activity1').tooltip({title: "Histidine decarboxylase", placement: "top"});
  $('#activity2').tooltip({title: "Carnosine N-methyltransferase", placement: "top"});

  let check_table_dict = {
    "AF_check": "AFtable",
    "AM_check": "AMtable",
    "L_check": "Ltable",
      };

  show_hide_tables("pw_form", check_table_dict);

});
