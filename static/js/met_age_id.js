import {initialise_list_table} from './metabolite_id_general.js';
import {get_lifestage} from './peak_tables_general';

require('./init_datatables.js');
const d3 = require('d3');
require('bootstrap/js/dist/tooltip');

function add_tooltips(obj){
  $('.NotDetected').tooltip({title: "A MS peak was not detected for this age/M/F combination", placement: "top"})
}

function headerTips(settings) {

  $(".col").each(function(){

    let $td = $(this);
    let header = $td.text();
    let head_split = header.split(" ");
    let tissue ="";
    let string ="";
    let ls="";

    if (head_split[0]=="Metabolite"){
      string = "Name of identified metabolite";
    }
    else {
      if (head_split[0]=="Whole"){
        string ="Whole (7 day old)"
      }
      else {
      string =`${head_split[0]} day old`
    }
      const header_words = head_split.length;
      const ls_check = header_words-1;
      ls = get_lifestage(head_split[ls_check])    }
      //Change the title attribute of the column to the string/tooltip info
    $td.attr({title: `${string} ${ls}`});
    $td.attr('data-bs-toggle', "tooltip");
    $td.attr('data-bs-placement', "top" );
});
/* Apply the tooltips */
$('[data-bs-toggle="tooltip"]').tooltip({
    container: 'body'
});

};


$(document).ready(function() {
    let met_table = initialise_list_table("met_list", min_value, mean_value, max_value, headerTips);
    add_tooltips(met_table);
});
