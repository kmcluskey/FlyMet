// require('./peak_tables_general.js');
import {initialise_pcompare_table, updatePeakSidePanel} from './peak_tables_general.js';

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
      string =`Fold change between Female and Male ${head_split[0]} tissue`;
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

  $(document).ready(function() {
  $("fieldset[class^='peak_details']").hide();

    let nd_title = " M and/or F data was not detected for this peak";
    let ajax_url = "peak_mf_compare_data";
    let peak_table = initialise_pcompare_table("peak_compare_list", min_value, mean_value, max_value, nd_title, ajax_url, headerTips);

        peak_table.on( 'click', 'tr', function () {
          updatePeakSidePanel(this);
        } );
  });
