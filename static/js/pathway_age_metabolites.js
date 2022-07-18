// require('./init_datatables')
require('bootstrap/js/dist/tooltip');
// const d3 = require('d3');

Awesomplete = require('awesomplete');
require('awesomplete/awesomplete.css');
require('../css/awesomechanges.css')

// import {updatePeakSidePanel2} from './pathway_metabolites_general.js';
import {pcompare_pathways_table, updatePeakSidePanel, get_lifestage} from './peak_tables_general.js';

//Fixme: This is the same function used in peak_age_compare - I'm just not sure how to import it here.

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


async function loadData(viewUrl) {
  try {
    const result = await $.getJSON(viewUrl);
    return result;
  } catch (e) {
    console.log(e);
  }
}

$(document).ready(function() {
  $("fieldset[class^='peak_details']").hide();
  //Method to add an autocomplete search function to the DB
  loadData((url)).then(function(data) {
    new Awesomplete(pathway_age_metabolites, {list: data.pathwayNames});
  });

  let nd_title = "This MS peak was not detected for this tissue/life stage combination";
  let peak_side_url = `peak_age_explorer/`;
  let peak_side_text =`Intensities for peak `;
  let met_url = `met_age_all/`;

  try {
    for (var i = 0; i < num_metabolites; i++) {

      let pwy_met_table = pcompare_pathways_table(`pwy_met_table_${i}`, min, mid, max, headerTips);
      // let pwy_met_table = initialise_pcompare_table2(`pwy_met_table_${i}`, min, mid, max);
      $("p[id^='pwy_id']").html(`<a href="pathway_age_search?pathway_age_search=${pathway_name}" data-bs-toggle="tooltip"
      title="${pathway_name} changes in FlyMet tissues" target="_blank">${pathway_name} in FlyMet</a>`);


      pwy_met_table.on( 'click', 'tr', function () {
        updatePeakSidePanel(this, peak_side_url, peak_side_text, met_url);
      } );
    }

  }
  catch(e) {

    if (e instanceof ReferenceError) {
    // Handle error as necessary
    console.log("waiting on table, caught", e);
    }
  }

  //Retrieve the datatables in order to have the columns delete throughout the page.
  var tables = $('table.display').DataTable( {
     retrieve: true,
     paging: false

    } );
    // When the column visibility changes on the first table, also change it on the others
    tables.table(0).on('column-visibility', function ( e, settings, colIdx, visibility ) {
        tables.tables(':gt(0)').columns( colIdx ).visible( visibility );
    } );

  $('#DSF').tooltip({title: "Matching Formulae in found Flymet", placement: "top"});
  $('#PWF').tooltip({title: "Unique Formulae in the Pathway", placement: "top"});
  $('#Cov').tooltip({title: "Dataset/Pathway formulae coverage", placement: "top"});

  console.log('number of metabolites', num_metabolites)
  console.log('pathway passed', pathway_name);
  console.log('url', url)

});
