require('./init_datatables.js');
const d3 = require('d3');
require('bootstrap/js/dist/tooltip');


function initialise_list_table(tableName, lowpoint, midpoint, highpoint, headerTips){
    const tName = '#'+tableName;
    const MIN_VAL = 3000;

    const dashType = $.fn.dataTable.absoluteOrderNumber({
                value: '-', position: 'bottom'
            });

    let table = $(tName).DataTable({
       "scrollY": "100vh",
       "scrollCollapse": true,
       "scrollX": true,
        colReorder: true,
        fixedheader: true,
        select: {
            style: 'single'
        },
        //code to override bootstrap and keep buttons on one line.
        dom: "<'row'<'col-sm-3'l><'col-sm-4'B><'col-sm-3'f>>" +
        "<'row'<'col-sm-12'rt>>" +
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
            {sType: "num-html", "targets":0},
            {
                "targets": '_all',
                'type': dashType,
                "createdCell": function (td, cellData, rowData, row, col) {

                    let $td = $(td);
                    // let $th = $td.closest('table').find('th').eq($td.index());
                    let $th = $(".col").eq($td.index());


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
                        const value = $td.text()
                        if (value == '-') {
                          $(td).addClass("NotDetected");
                        }

                        else if (value > 100){ //it is intensity data
                            const num = parseFloat(value).toExponential(2)
                            $td.empty();
                            $td.append(num);
                            $(td).addClass("data");
                          }

                    if ($th.text().includes('Metabolite')){
                      $(td).addClass("maxpx300")
                    }
                }
            }
        ],
        // Add the tooltips to the dataTable header
        "initComplete": headerTips

    })

//Return the table so that the it is resuable.
    return table;
}

export {initialise_list_table}
