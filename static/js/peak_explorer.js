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
  $("fieldset[class^='peak_details']").hide();

  let nd_title = "A MS peak was not detected for this tissue/life stage combination";
  let ajax_url = `peak_data/${peak_list}`;
  let peak_side_url = `peak_ex_compare/`;
  let peak_side_text =`Compare tissues for peak `;
  let met_url = `met_ex_all/`;
  upDateFilteredPeaks(peak_side_url);

  let peak_table = initialise_pcompare_table("peak_list", min_value, mean_value, max_value, nd_title, ajax_url, headerTips);
      peak_table.on( 'click', 'tr', function () {
        updatePeakSidePanel(this, peak_side_url, peak_side_text, met_url);
      } );

});

function upDateFilteredPeaks(peak_side_url){
  console.log("In here")
  let pathArray = window.location.pathname.split('/');
  let filteredPeaks = pathArray.slice(-1);
  // let peak_mf_url = `peak_mf_compare/`;
  let filtered_url = peak_side_url+filteredPeaks
  // let filtered_mf = peak_mf_url+filteredPeaks

  $("a[id='PeakCompare']").html(`<a href="${filtered_url}" target="_blank" >Tissue/Whole Comparisons</a>`);
  // $("a[id='MFCompare']").html(`<a href="${filtered_mf}" target="_blank" >M/F Comparisons</a>`);

}
