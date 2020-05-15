require('./init_datatables')
require('bootstrap/js/dist/tooltip');
const d3 = require('d3');
import {initialise_table} from './flymet_tables';
import {show_hide_tables} from './flymet_tables';

Awesomplete = require('awesomplete');
require('awesomplete/awesomplete.css');
require('../css/awesomechanges.css')

// const url = `/met_explore/pathway_search_data/${pwy_id}`
// fetch(url)
// .then(res => res.json())//response type
// .then(handleUpdate);


function initialise_pcompare_table(tableName, lowpoint, midpoint, highpoint){
    // let t0 = performance.now();
    const tName = '#'+tableName;
    console.log("tablename", tName)
    console.log (lowpoint, midpoint, highpoint)
    // const MIN_VAL = -7;
    // const peak_data = document.getElementById('pwy_met_table').getAttribute('url');
//
//     console.log("Peak data ", peak_data)
//
    let table = $(tName).DataTable({

      drawCallback: function(settings){
          /* Add some tooltips for demonstration purposes */
          $('.NotDetected').tooltip({title: "A MS peak was not detected for this tissue/life stage combination", placement: "top"})
      },

        // responsive: true,
        "scrollY": "100vh",
        "scrollCollapse": true,
        "scrollX": true,
        fixedheader: true,
        colReorder: true,
        // ajax: {
        //   url: `/met_explore/metabolite_pathway_data/${pwy_id}`,
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
            {

                "targets": '_all',
                "createdCell": function (td, cellData, rowData, row, col) {

                    let $td = $(td);
                    // console.log($td.text())
                    let $th = $(".col").eq($td.index());

                    const colorScale = d3.scaleLinear()
                        .domain([lowpoint, midpoint, highpoint])
                        .range(["#1184fc", "#D6DCE6", "#8e3b3d"]);

                    //If the column header doesn't include the string Tissue then colour the column.

                    if (!($th.text().includes('Peak ID') || $th.text().includes('m/z') || $th.text().includes('RT'))) {
                        if (!(isNaN(cellData))){ //if the value of the cell is a number then colour it.
                            // if (cellData==0.00){
                            //   cellData = MIN_VAL //Can't pass zero to the log so choose minimum value
                            // };
                            const colour = colorScale(cellData);
                            $(td).css('background-color', colour)
                        }
                    }
                    // Format the column numbers
                    //Ignore for the peak ID
                    if ($th.text().includes('Peak ID')){
                      $(td).addClass('"text-center"')
                    }
                    // If m_z or RT reformat the number to 2 dec places.
                   else if ($th.text().includes('RT')){
                      const value = $td.text()
                      const num = parseFloat(value).toFixed(2)
                      $td.empty();
                      $td.append(num);
                    }
                    else if ($th.text().includes('m/z')){
                      const value = $td.text()
                      const num = parseFloat(value).toFixed(4)
                      $td.empty();
                      $td.append(num);
                    }

                    // If the number is some of the tissue data
                    else {
                      const value = $td.text()
                      if (value == '-') {
                        $(td).addClass("NotDetected");
                      }
                      else {
                      const num = parseFloat(value).toFixed(2)
                      $td.empty();
                      $td.append(num);
                      $(td).addClass("data");
                    }
                    }
                    }
                  }
        ],
        // Add the tooltips to the dataTable header
        "initComplete": function(settings){

                    $(".col").each(function(){

                      let $td = $(this);
                      let header = $td.text();
                      let head_split = header.split(" ");
                      let string ="";
                      let ls="";

                      if (head_split[0]=="m/z")
                        string = "mass-to-charge ratio";
                      else if (head_split[0]=="Peak")
                        string ="";
                      else if (head_split[0]=="RT")
                        string ="Retention Time";
                      else
                        string =`Fold change between ${head_split[0]} tissue from`;
                        const header_words = head_split.length;
                        const ls_check = header_words-1;
                        ls = get_lifestage(head_split[ls_check])

                      //Change the title attribute of the column to the string/tooltip info
                      $td.attr({title: `${string} ${ls} and Whole ${ls} flies`});
                      $td.attr('data-toggle', "tooltip");
                      $td.attr('data-placement', "top" );
                  });
                  /* Apply the tooltips */
                  $('[data-toggle="tooltip"]').tooltip({
                      container: 'body'
                  });
              },
    })

    return table;
}

async function loadData(viewUrl) {
  try {
    const result = await $.getJSON(viewUrl);
    return result;
  } catch (e) {
    console.log(e);
  }
}

function get_lifestage(ls_string){

  let ls = "";
  if (ls_string=="(F)")
    ls ="Females";
  else if (ls_string=="(M)")
      ls ="Males";
  else if (ls_string=="(L)")
        ls ="Larvae";

  return ls
}


$(document).ready(function() {

  //Method to add an autocomplete search function to the DB
  loadData((url)).then(function(data) {
    new Awesomplete(pathway_search, {list: data.pathwayNames});
  });

  try {
    for (var i = 0; i < num_metabolites; i++) {
      console.log('printing i',i)

      let pwy_met_table = initialise_pcompare_table(`pwy_met_table_${i}`, min, mid, max);
    }

    // add_met_tooltips(pwy_met_table, metabolite);
    // add_table_tooltip(pwy_met_table);

    // met_table.on( 'click', 'tr', function () {
    //   updateMetSidePanel(this, metabolite);
    // } )
  }
  catch(e) {

    if (e instanceof ReferenceError) {
    // Handle error as necessary
    console.log("waiting on table, caught", e);
    }
  }
  // //$("fieldset[class^='peak_details']").hide();
  //
  // initialise_table("pw_table_AF",-10.0, 0.0, 10);
  // initialise_table("pw_table_AM",-10.0, 0.0, 10);
  // initialise_table("pw_table_L",-10.0, 0.0, 10);
  //
  // $('#activity1').tooltip({title: "Histidine decarboxylase", placement: "top"});
  // $('#activity2').tooltip({title: "Carnosine N-methyltransferase", placement: "top"});
  //
  // let check_table_dict = {
  //   "AF_check": "AFtable",
  //   "AM_check": "AMtable",
  //   "L_check": "Ltable",
  //     };
  //
  // show_hide_tables("pw_form", check_table_dict);
  console.log('number of metabolites', num_metabolites)
  console.log('pathway passed', pathway_name);
  console.log('url', url)

});
