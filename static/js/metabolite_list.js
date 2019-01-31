require('popper.js');
require('bootstrap');
const d3 = require('d3');
require('datatables.net');

require('datatables.net-buttons-bs4/css/buttons.bootstrap4.min.css');
require('datatables.net-bs4/css/dataTables.bootstrap4.min.css');
require('datatables.net-scroller-bs4/css/scroller.bootstrap4.min.css');
require('datatables.net-select-bs4/css/select.bootstrap4.min.css');

require('pdfmake/build/pdfmake.js');
require('pdfmake/build/vfs_fonts.js');

require( 'datatables.net-bs4' );
require( 'datatables.net-buttons-bs4');
require( 'datatables.net-buttons/js/buttons.colVis.js' );  // Column visibility
require( 'datatables.net-buttons/js/buttons.html5.js');
require( 'datatables.net-buttons/js/buttons.print.js' );
require( 'datatables.net-fixedcolumns-bs4' );
require( 'datatables.net-fixedheader-bs4' );
require( 'datatables.net-responsive-bs4' );
require( 'datatables.net-scroller-bs4' );
require( 'datatables.net-select-bs4' );
require( 'datatables.net-plugins/sorting/scientific.js' );

function initialise_list_table(tableName, lowpoint, midpoint, highpoint){
    const tName = '#'+tableName;
    let table = $(tName).DataTable({
        responsive: true,

        "scrollY": "100vh",
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

                    const colorScale = d3.scaleLog()
                        .domain([lowpoint, midpoint, highpoint])
                        .range(["#1184fc", "#D6DCE6", "#8e3b3d"]);

                    //If the column header doesn't include the string Tissue then colour the column.
                    if (!($th.text().includes('Metabolite'))) {
                        if (!(isNaN(cellData))){ //if the value of the cell is a number then colour it.
                            const colour = colorScale(cellData);
                            $(td).css('background-color', colour)

                        }
                    }
                }
            }
        ]
    });
//Return the table so that the it is resuable.
    return table;
}

$(document).ready(function() {

    let met_table = initialise_list_table("met_list", 2000000, 672500000, 1340000000);

});
