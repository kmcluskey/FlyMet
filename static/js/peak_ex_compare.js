import {initialise_pcompare_table, updatePeakSidePanel} from './peak_compare_general.js';

function headerTips(settings) {

  $(".col").each(function(){

    let $td = $(this);
    let header = $td.text();
    let head_split = header.split(" ");
    let tissue ="";
    let string ="";
    let ls="";

    if (head_split[0]=="m/z"){
      string = "mass-to-charge ratio";
    }
    else if (head_split[0]=="Peak"){
      string ="";
    }
    else if (head_split[0]=="RT"){
      string ="Retention Time";
    }
    else {
      tissue =`Fold change between ${head_split[0]} tissue from`;
      const header_words = head_split.length;
      const ls_check = header_words-1;
      ls = get_lifestage(head_split[ls_check])
      string = `${tissue} ${ls} and Whole ${ls} flies`
    }
      //Change the title attribute of the column to the string/tooltip info
    $td.attr({title: `${string}`});
    $td.attr('data-toggle', "tooltip");
    $td.attr('data-placement', "top" );
});
/* Apply the tooltips */
$('[data-toggle="tooltip"]').tooltip({
    container: 'body'
});

};


function get_lifestage(ls_string){

  let ls = "";
  if (ls_string=="(F)")
    ls ="Females";
  else if (ls_string=="(M)")
      ls ="Males";
  else if (ls_string=="(L)")
        ls ="Larvae";

  return ls
};

$(document).ready(function() {
    $("fieldset[class^='peak_details']").hide();

    let nd_title = "This MS peak was not detected for this tissue/life stage combination";
    let ajax_url = "peak_compare_data";
    let peak_table = initialise_pcompare_table("peak_compare_list", min_value, mean_value, max_value, nd_title, ajax_url, headerTips);

      peak_table.on( 'click', 'tr', function () {
        updatePeakSidePanel(this);
      } );

});
