// A function to initialise a standard table with buttons. The midpoint is the neutral value
// and is most likely a temporary way to calculate significance in the data for display purposes

require ('./init_datatables')
const d3 = require('d3');

import {singleMet_intensity_chart} from './flymet_highcharts.js';


function initialise_table(tableName, lowpoint, midpoint, highpoint, project, data_index){
    const tName = '#'+tableName;
    console.log(tName)
    let table = $(tName).DataTable({
        //responsive: true,

        "scrollY": "40vh",
        "scrollCollapse": true,
        "scrollX": true,
        select: {
            style: 'single'
        },
        dom: //code to override bootstrap and keep buttons on one line.
        "<'row'<'col-sm-3'l><'col-sm-4'B><'col-sm-3'f>>" +
        "<'row'<'col-sm-12'tr>>" +
        "<'row'<'col-sm-6'i><'col-sm-6'p>>",
        buttons: [ 'copy',
            {
                extend: 'collection',
                text: 'Export',
                buttons: [ 'csv', 'pdf' ]
            }
        ],

        //Code to add the colours to the data - temporary numbers have been added.
        "columnDefs": [
            {className: "dt-center", "targets":"_all"},
            {type: "num", "targets":data_index},

            {
                "targets": '_all',
                "createdCell": function (td, cellData, rowData, row, col) {
                    let $td = $(td);
                    //find the table headers with class=data
                    let $th = $td.closest('table').find('th.data').eq($td.index());

                    //console.log($th.text())

                    const colorScale = d3.scaleLinear()
                        .range(["#1184fc", "#D6DCE6", "#8e3b3d"])
                        .domain([lowpoint, midpoint, highpoint]);

                    //If the column header doesn't include the string Tissue then colour the column.
                    if (!($th.text().includes(project))) {
                        if (!(isNaN(cellData))){ //if the value of the cell is a number then colour it.
                            const colour = colorScale(cellData);
                            $(td).css('background-color', colour);
                        }
                    }
                }
            }
        ]
    });
//Return the table so that the it is resuable.
    return table;
}

//A simple datatable for showing colours with limited funtionality.
function init_met_side_table(tableName, lowpoint, midpoint, highpoint){

    const tName = '#'+tableName;

    console.log(tName)

    let table = $(tName).DataTable({
        responsive: true,
        "bPaginate": false,
        "bFilter": false,
        "bInfo": false,
        "columnDefs": [
            {className: "dt-center", "targets":"_all"},
            {
                "targets": '_all',
                "createdCell": function (td, cellData, rowData, row, col) {
                    let $td = $(td);
                    //find the table headers
                    var $th = $td.closest('table').find('th').eq($td.index());

                    const colorScale = d3.scaleLinear()
                        .range(["#1184fc", "#D6DCE6", "#8e3b3d"])
                        .domain([lowpoint, midpoint, highpoint]);

                    //If the column header doesn't include the string Tissue then colour the column.
                    if ($th.text().includes('FC')) {
                        if (!(isNaN(cellData))){
                            const colour = colorScale(cellData);
                            $(td).css('background-color', colour);
                        }
                    }
                }
            }
        ]

    });
    console.log("returning table")
    return table;
}

//This will hide all the tables under a certain form and show the first by default.
function show_hide_tables(pw_form, dict){

    for(var check_key in dict) {
        var pw_table = dict[check_key];
        // console.log(check_key);
        // console.log(pw_table);
        let form = $('#'+pw_form), //get the specific form
            checkbox =$('#'+check_key),
            table=$('#'+pw_table);

        table.hide();
        checkbox.on('click', function() {
            if($(this).is(':checked')) {
                table.show();
                table.find('input').attr('required', true);
            } else {
                table.hide();
                table.find('input').attr('required', false);
            };

        })

        //Get the first table and checkbox passed and chack and show them by default
        let first = Object.keys(dict)[0];
        let first_table = Object.values(dict)[0]

        $('#'+first).prop('checked', true);
        $('#'+first_table).show();

    }
}

function updateMetSidePanel(obj, metabolite){
  let tissue_name = $(obj).children().first().text();

  console.log(tissue_name)

  const series_data = [ { xAxis: 0, name: "Life Stages", id: "master_1", data: null},
  { name: 'IQR',
  type: 'errorbar',
  linkedTo: "master_1",
  data: null,
  marker: {
    enabled: false
  },
  pointWidth: 15, // Sets the width of the error bar -- Must be added, otherwise the width will change unexpectedly #8558
  pointRange: 0,  //Prevents error bar from adding extra padding on the X-axis
  tooltip: {
    pointFormat: ''
  }
  //stemWidth: 10,
  //whiskerLength: 5
}
];

const drilldown_data = [
  {
    xAxis: 1,
    name: "F",
    id: "1",
    data: null
  },
  {
    xAxis: 1,
    name: "FW",
    id: "2",
    data: null
  },
  {
    xAxis: 1,
    name: "M",
    id: "3",
    data: null
  },
  {
    xAxis: 1,
    name: "MW",
    id: "4",
    data: null
  },
  {
    xAxis: 1,
    name: "L",
    id: "5",
    data: null
  },
  {
    xAxis: 1,
    name: "LW",
    id: "6",
    data: null
  },

];

const handleUpdate = function(returned_data) {

  const probability = returned_data.probability;

  series_data[0].data = returned_data.series_data;
  series_data[1].data = returned_data.error_bar_data;

  // Fill in the drill down data for each lifestage.
  const returned_drill =  returned_data.drilldown_data;
  var i;
  for (i = 0; i < returned_drill.length; i++) {
    drilldown_data[i].data = returned_data.drilldown_data[i];
  }

  // Send on to highchart function
  singleMet_intensity_chart('highchart', series_data, drilldown_data);
  // Add tooltips to the highchart
  add_highchart_tooltips(probability);
};



//const url = 'http://127.0.0.1:8000/met_explore/met_search_highchart_data/'+ tissue_name+'/'+ metabolite;
const url = `/met_explore/met_search_highchart_data/${analysis_id}/${tissue_name}/${metabolite}`
fetch(url)
.then(res => res.json())//response type
.then(handleUpdate);

// find all the paragraphs with id peak in the side panel
$("fieldset[id='click_info']").hide();
$("fieldset[class^='peak_details']").show();
$("p[id^='tissue_type']").text('Intensities in ' + tissue_name);

// Add table header tooltips --these are temporary.
//KMCL: These tool tips have to be replaced with something responsive - i.e. where the buttons change depending on the data.
function add_highchart_tooltips(probability){
  $('#I').tooltip({title: "MS peak has been Identified as " + metabolite + " using a library standard", placement: "top"});
  $('#F').tooltip({title: "MS/MS Fragmentation data suggests that a peak is "+ probability + "% likely to be "+ metabolite, placement: "top"});
  $('#A').tooltip({title: "This peak, annotated as Histidine, also annotates 15 other compounds", placement: "top"});
};
};

function add_met_tooltips(obj){

    $('.AM_met_WT_ratio').tooltip({title: "Fold Change of metabolite Intensity in Adult Male vs Whole Fly", placement: "top"});
    $('.AF_met_WT_ratio').tooltip({title: "Fold change of metabolite Intensity in Adult Female vs Whole Fly", placement: "top"});
    $('.L_met_WT_ratio').tooltip({title: "Fold change of metabolite Intensity in Larvae vs Whole Fly", placement: "top"});

}


function updateEnzymeSidePanel(obj){
    let tissue_name = $(obj).children().first().text();

    $("fieldset[id='click_info']").hide();
    $("fieldset[class^='reaction_details']").show();
    $("p[id^='tissue_type']").text(tissue_name+' metabolites found in Histamine Biosynthesis. ');
    $("legend[class^='tissue']").text(tissue_name);
}

export {initialise_table,
        add_met_tooltips,
        init_met_side_table,
        show_hide_tables,
        updateMetSidePanel,
        updateEnzymeSidePanel,
      }
