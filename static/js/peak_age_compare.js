import {initialise_pcompare_table, updatePeakSidePanel, get_lifestage} from './peak_tables_general.js';

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
      tissue =`Fold change between ${head_split[0]} day old`;
      const header_words = head_split.length;
      const ls_check = header_words-1;
      ls = get_lifestage(head_split[ls_check])
      string = `${tissue} ${ls} and Whole (7 day old) ${ls}`
      }
      //Change the title attribute of the column to the string/tooltip info
    $td.attr({title: `${string}`});
    $td.attr('data-bs-toggle', "tooltip");
    $td.attr('data-bs-placement', "top" );
});
/* Apply the tooltips */
$('[data-bs-toggle="tooltip"]').tooltip({
    container: 'body'
});

};

$(document).ready(function() {
    $("fieldset[class^='peak_details']").hide();
    console.log("peak compare list", peak_compare_list)

    let nd_title = "This MS peak was not detected for this age of fly";
    let ajax_url = `peak_age_compare_data/${peak_compare_list}`;
    let peak_side_url = `peak_age_explorer/`;
    let peak_side_text =`Age intensities for peak `;
    let met_url = `met_age_all/`;


    let peak_table = initialise_pcompare_table("peak_list", min_value, mean_value, max_value,
    nd_title, ajax_url, headerTips);

      peak_table.on( 'click', 'tr', function () {
        updatePeakSidePanel(this, peak_side_url, peak_side_text, met_url);
      } );
});

export {headerTips}
