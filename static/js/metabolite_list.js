require('./init_datatables.js');
const d3 = require('d3');


function initialise_list_table(tableName, lowpoint, midpoint, highpoint){
    const tName = '#'+tableName;
    const MIN_VAL = 3000;
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
                        .domain([MIN_VAL, midpoint, highpoint])
                        .range(["#1184fc", "#D6DCE6", "#8e3b3d"]);

                    //If the column header doesn't include the string Tissue then colour the column.
                    if (!($th.text().includes('Metabolite'))) {
                        if (!(isNaN(cellData))){ //if the value of the cell is a number then colour it.
                            if (cellData==0.00){
                              cellData = MIN_VAL //Can't pass zero to the log so choose minimum value
                            };
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
    // let met_table = initialise_list_table("met_list", 2000000, 672500000, 1340000000);
    let met_table = initialise_list_table("met_list", min_value, mean_value, max_value);

});
