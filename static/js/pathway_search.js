import {enableTooltips, updatePathwayInfo, updateReactomePathway} from './pathways_general.js';
// import {initialise_table} from './flymet_tables';

Awesomplete = require('awesomplete');
require('awesomplete/awesomplete.css');
require('../css/awesomechanges.css')
require('bootstrap/js/dist/tooltip');
require ('./init_datatables')
const d3 = require('d3');

function initialise_pwy_table(tableName, lowpoint, midpoint, highpoint){
    let t0 = performance.now();
    const tName = '#'+tableName;
    console.log("tablename", tName)
    const MIN_VAL = 3000;
    // const pals_data = document.getElementById('pals_data').getAttribute('url');
    const nmType = $.fn.dataTable.absoluteOrderNumber({
                    value: 'nm', position: 'bottom'
                });
    let table = $(tName).DataTable({

        "scrollY": "100vh",
        "scrollCollapse": true,
        scrollX: true,
        fixedheader: true,
        colReorder: true,
        // ajax: {
        //   url: "/met_explore/pals_data",
        //   cache: true,  //This is so we can use the cached data otherwise DT doesn't allow it.
        // },

        select: {
            style: 'single'
        },
        //code to override bootstrap and keep buttons on one line.
        dom: "<'row'<'col-sm-3'l><'col-sm-4'B><'col-sm-3'f>>" +
        "<'row'<'col-sm-12'rt>>" +
        "<'row'<'col-sm-6'i><'col-sm-6'p>>",
        buttons: [ 'colvis', 'copy',

            {
                extend: 'collection',
                text: 'Export',
                buttons: [ 'csv', 'pdf' ]
            }
        ],
        //Code to add the colours to the data - temporary numbers have been added.

        "columnDefs": [
            {className: "dt-center", "targets":"_all"},
            {className: "px300", "targets": "_all"}, // Here - try and make this a maximum column width
            {
                "targets": '_all',
                'type': nmType,
                "createdCell": function (td, cellData, rowData, row, col) {

                    let $td = $(td);
                    // console.log($td.text())
                    let $th = $(".col").eq($td.index());

                    const colorScale = d3.scaleLinear()
                        .domain([lowpoint, midpoint, highpoint])
                        .range(["#1184fc", "#D6DCE6", "#8e3b3d"]);

                    //If the column header doesn't include the string Tissue then colour the column.

                    if (!($th.text().includes('Tissue-Type'))) {
                        if (!(isNaN(cellData))){
                            const colour = colorScale(cellData);
                            $(td).css('background-color', colour)
                         }
                    }
                    // Format the column numbers
                    //Ignore for the peak ID
                    if ($th.text().includes('Tissue-Type')){
                      $(td).addClass("text-centre")
                      $(td).addClass("px300")
                    }
                   //  // If m_z or RT reformat the number to 2 dec places.
                   // else if ($th.text().includes('PW F')){
                   //    const value = $td.text()
                   //    const num = parseInt(value)
                   //    $td.empty();
                   //    $td.append(num);
                   //  }
                   //  else if ($th.text().includes('DS F')){
                   //    const value = $td.text()
                   //    const num = parseInt(value)
                   //    $td.empty();
                   //    $td.append(num);
                   //  }
                   //
                   //  else if ($th.text().includes('F Cov')){
                   //    const value = $td.text()
                   //    const num = parseFloat(value).toFixed(1)
                   //    $td.empty();
                   //    $td.append(num);
                   //    $td.append(' %');
                   //
                   //  }

                    // If the number is some of the tissue data

                    else {
                      const value = $td.text()
                      if (value == 'nm') {
                        $(td).addClass("notMeasured");
                      }
                        else {
                          const num = parseFloat(value).toExponential(1)
                          $td.empty();
                          $td.append(num);
                          $(td).addClass("data");
                        }
                    }

                    // else {
                    //   const value = $td.text()
                    //   const num = parseFloat(value).toExponential(1)
                    //   $td.empty();
                    //   $td.append(num);
                    //   $(td).addClass("data");
                    // }
                    }
                  },
                  //
                  // {
                  //   targets:[0], // Hide the reactome ID but we still might want to use it
                  //   "visible": false
                  // },
        ],
        // Add the tooltips to the dataTable header
        // "initComplete": function(settings){
        //
        //             $(".col").each(function(){
        //               let $td = $(this);
        //               let header = $td.text().trim();
        //               let head_split = header.split(" ");
        //               let string ="";
        //               let ls="";
        //               if (header=="Pathway name")
        //                 string = '';
        //               else if (header=="PW F")
        //                 string = "No. unique formulae found in the pathway";
        //               else if (header=="DS F")
        //                 string ="No. unique formulae from the pathway found in the dataset";
        //               else if (header=="F Cov")
        //                 string ="Pathway formula coverage in dataset";
        //               else {
        //                 string =`Changes in ${head_split[0]} tissue from`;
        //                 const header_words = head_split.length;
        //                 const ls_check = header_words-1;
        //                 ls = get_lifestage(head_split[ls_check]);
        //                 string=`${string} ${ls} compared to Whole ${ls} flies`;}
        //
        //               //Change the title attribute of the column to the string/tooltip info
        //               // console.log("This is the string ", string)
        //               $td.attr({title: `${string}`});
        //               $td.attr('data-toggle', "tooltip");
        //               $td.attr('data-placement', "top" );
        //           });
        //
        //           enableTooltips();
        //       },
    })

    let t1 = performance.now();
    console.log("This is the Time to initialise the table " + (t1 - t0) + " milliseconds.")
    console.log("returning table")
    return table;
  }

  function add_table_tooltips(obj){
    $('.notMeasured').tooltip({title: "A sample has not been measured for this tissue/life stage combination", placement: "top"})
  }

  function add_pwy_tooltips(obj, pathway_name){

    $('#AF-pvalue').tooltip({title: "P-value of changes in the metabolites of " + pathway_name + " between female tissue & female whole Flies", placement: "top"});
    $('#AM-pvalue').tooltip({title: "P-value of changes in the metabolites of " + pathway_name + " between male tissues & male whole Flies", placement: "top"});
    $('#L-pvalue').tooltip({title: "P-value of changes in the metabolites of " + pathway_name+ " between larvae tissue & whole larvae", placement: "top"});

  }

function updatePathwayDetails(obj) {

  const handleUpdate = function(returned_data) {
    updatePathwayInfo(returned_data, pathway_name)
    updateReactomePathway(pathway_id, pathway_name, reactome_token)
    $("[class^='pathway_details']").show();

};
  //Update the bottom panel with a diagram using the Reactome ID.
  console.log("Pathway ID ", pathway_id)
  const url = `/met_explore/metabolite_pathway_data/${pathway_id}`
  fetch(url)
  .then(res => res.json())//response type
  .then(handleUpdate);


  $("p[id^='pwy_id']").html(`<a href="pathway_metabolites?pathway_metabolites=${pathway_name}" data-toggle="tooltip"
  title="FlyMet metabolites and peaks found in ${pathway_name}" target="_blank">${pathway_name} in FlyMet</a>`);

  enableTooltips();

}

async function loadData(viewUrl) {
  try {
    const result = await $.getJSON(viewUrl);
    return result;
  } catch (e) {
    console.log(e);
  }
}

$(document).ready(function() {
  $("[class^='pathway_details']").hide();
  $("#diagram_info").hide();


  //Method to add an autocomplete search function to the DB
  loadData((url)).then(function(data) {
    new Awesomplete(pathway_search, {list: data.pathwayNames});
  });
  // If the pathway_id has been returned from tne page
  if (pathway_id) {
    try {
      let pwy_table = initialise_pwy_table('pwy_table', pals_min, pals_mid, pals_max);
      add_table_tooltips(pwy_table);
      add_pwy_tooltips(pwy_table, pathway_name)

      updatePathwayDetails(this);
  //
  //
  //   // for (var i = 0; i < num_metabolites; i++) {
  //   //   updatePeakSidePanel(this);
  //   //   let pwy_met_table = initialise_pcompare_table(`pwy_met_table_${i}`, min, mid, max);
  //   //
  //   //   pwy_met_table.on( 'click', 'tr', function () {
  //   //
  //   //   } );
  //   //
  //   // }
  //
  }
  catch(e) {
  //
    if (e instanceof ReferenceError) {
  //   // Handle error as necessary
   console.log("waiting on pathway to be passed, caught", e);
    }
  }
}
  console.log('pathway passed', pathway_name);
  console.log('url', url)

});
