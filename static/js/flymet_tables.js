// A function to initialise a standard table with buttons. The midpoint is the neutral value
// and is most likely a temporary way to calculate significance in the data for display purposes

require ('./init_datatables')
const d3 = require('d3');



function initialise_table(tableName, lowpoint, midpoint, highpoint){
    const tName = '#'+tableName;
    console.log(tName)
    let table = $(tName).DataTable({
        responsive: true,

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
                    if (!($th.text().includes('Tissue'))) {
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

//Update the metabolite side panel depending on which row is selected.
//Let tissue name = the first text sent back from the row (more or less)
// function updateMetSidePanel(obj){
//     let tissue_name = $(obj).children().first().text();
//
//     // find all the paragraphs with id peak in the side panel
//
//     $("fieldset[id='click_info']").hide();
//     $("fieldset[class^='peak_details']").show();
//     $("p[id^='tissue_type']").text('Intensities in ' +tissue_name);
//
//
//     singleMet_intensity_chart('highchart');
//     singleMet_intensity_chart('highchart1');
//     singleMet_intensity_chart('highchart2');
//
//     // Add table header tooltips --these are temporary.
//     //KMCL: These tool tips have to be replaced with something responsive - i.e. where the buttons change depending on the data.
//
//     $('#I').tooltip({title: "MS peak has been Identified as Histidine using a library standard", placement: "top"});
//     $('#I2').tooltip({title: "MS peak has been Identified as Histidine using a library standard", placement: "top"});
//     $('#F').tooltip({title: "MS/MS Fragmentation data suggests that a peak is 96.2% likely to be Histidine", placement: "top"});
//     $('#F1').tooltip({title: "MS/MS Fragmentation data suggests that a peak is 99% likely to be Histidine", placement: "top"});
//     $('#A').tooltip({title: "This peak, annotated as Histidine, also annotates 15 other compounds", placement: "top"});
//     $('#A1').tooltip({title: "This peak, annotated as Histidine, also annotates 4 other compounds", placement: "top"});
//     $('#A2').tooltip({title: "This peak, annotated as Histidine, also annotates 47 other compounds", placement: "top"});
//     $('#F0').tooltip({title: "There is no fragmenetation data associated with this peak", placement: "top"});
//
//
// }
//
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


export {initialise_table, init_met_side_table, show_hide_tables, updateEnzymeSidePanel, add_met_tooltips }
