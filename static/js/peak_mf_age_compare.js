// require('./peak_tables_general.js');
import {initialise_pcompare_table, updatePeakSidePanel} from './peak_tables_general.js';

function headerTips(settings) {

  $(".col").each(function(){

    let $td = $(this);
    let header = $td.text();
    let head_split = header.split(" ");
    let string ="";

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
      string =`Fold change between Female and Male ${head_split[0]} day old flies`;
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
    let ajax_url = "peak_mf_age_data";
    let peak_side_url = `peak_age_explorer/`;
    let peak_side_text =`Age intensities for peak `
    let met_url = `met_age_all/`;

    let peak_table = initialise_pcompare_table("peak_list", min_value, mean_value, max_value, nd_title, ajax_url, headerTips);

        peak_table.on( 'click', 'tr', function () {
          updatePeakSidePanel(this, peak_side_url, peak_side_text, met_url);
        } );
  });
