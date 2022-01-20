import {initialise_list_table} from './metabolite_id_general.js';
import {get_lifestage} from './peak_tables_general';

require('./init_datatables.js');
const d3 = require('d3');
require('bootstrap/js/dist/tooltip');


function headerTips(settings) {

  $(".col").each(function(){

    let $td = $(this);
    let header = $td.text();
    let head_split = header.split(" ");
    let tissue ="";
    let string ="";
    let ls="";

    if (head_split[0]=="Metabolite"){
      string = "Identified metabolite name";
    }
    else {
      string =`${head_split[0]} tissue from`;
      const header_words = head_split.length;
      const ls_check = header_words-1;
      ls = get_lifestage(head_split[ls_check])    }
      //Change the title attribute of the column to the string/tooltip info
    $td.attr({title: `${string} ${ls}`});
    $td.attr('data-toggle', "tooltip");
    $td.attr('data-placement', "top" );
});
/* Apply the tooltips */
$('[data-toggle="tooltip"]').tooltip({
    container: 'body'
});

};


$(document).ready(function() {
    let met_table = initialise_list_table("met_list", min_value, mean_value, max_value, headerTips);
    add_tooltips(met_table);

});

function add_tooltips(obj){
  $('.NotDetected').tooltip({title: "A MS peak was not detected for this tissue/life-stage combination", placement: "top"})
}
