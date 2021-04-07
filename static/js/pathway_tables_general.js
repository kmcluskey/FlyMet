require('./init_datatables.js');
const d3 = require('d3');
require('bootstrap/js/dist/tooltip');


function initialise_pwy_table(tableName, lowpoint, midpoint, highpoint, project) {
    let t0 = performance.now();
    const tName = '#' + tableName;
    console.log("tablename", tName)
    console.log("Project", project)
    const MIN_VAL = 3000;
    // const pals_data = document.getElementById('pals_data').getAttribute('url');
    const nmType = $.fn.dataTable.absoluteOrderNumber({
        value: 'nm', position: 'bottom'
    });
    let table = $(tName).DataTable({

        fixedheader: true,
        colReorder: true,
        // select: {
        //     style: 'single'
        // },
        //code to override bootstrap and keep buttons on one line.
        dom: "<'row'<'col-sm-3'l><'col-sm-4'B><'col-sm-3'f>>" +
            "<'row'<'col-sm-12'rt>>" +
            "<'row'<'col-sm-6'i><'col-sm-6'p>>",
        buttons: ['colvis', 'copy',

            {
                extend: 'collection',
                text: 'Export',
                buttons: ['csv', 'pdf']
            }
        ],
        //Code to add the colours to the data - temporary numbers have been added.

        "columnDefs": [
            {className: "dt-center", "targets": "_all"},
            // {className: "px300", "targets": "_all"}, // Here - try and make this a maximum column width
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

                    if (!($th.text().includes(project))) {
                        if (!(isNaN(cellData))) {
                            const colour = colorScale(cellData);
                            $(td).css('background-color', colour)
                        }
                    }
                    // Format the column numbers
                    //Ignore for the peak ID
                    if ($th.text().includes(project)) {
                        $(td).addClass("text-centre")
                    }

                    // If the number is some of the tissue data

                    else {
                        const value = $td.text()
                        if (value == 'nm') {
                            $(td).addClass("notMeasured");
                        } else {
                            let num = parseFloat(value).toExponential(1);
                            if (isNaN(num)) { // if can't be parsed to float, leave the value as it is
                                num = value;
                            }
                            $td.empty();
                            $td.append(num);
                            $(td).addClass("data");
                        }
                    }
                }
            },

        ],

    })

    let t1 = performance.now();
    console.log("This is the Time to initialise the table " + (t1 - t0) + " milliseconds.")
    console.log("returning table")
    return table;
}


function initialise_pals_table(tableName, lowpoint, midpoint, highpoint, data_url, met_ex_url) {
    let t0 = performance.now();
    const tName = '#' + tableName;
    console.log("tablename", tName)
    const MIN_VAL = 3000;
    const pals_age_data = document.getElementById(`${data_url}`).getAttribute('url');

    let table = $(tName).DataTable({

        "scrollY": "100vh",
        "scrollCollapse": true,
        scrollX: true,
        fixedheader: true,
        colReorder: true,
        ajax: {
            url: `/met_explore/${data_url}`,
            cache: true,  //This is so we can use the cached data otherwise DT doesn't allow it.
        },

        select: {
            style: 'single'
        },
        //code to override bootstrap and keep buttons on one line.
        dom: "<'row'<'col-sm-3'l><'col-sm-4'B><'col-sm-3'f>>" +
            "<'row'<'col-sm-12'rt>>" +
            "<'row'<'col-sm-6'i><'col-sm-6'p>>",
        buttons: ['colvis', 'copy',

            {
                extend: 'collection',
                text: 'Export',
                buttons: ['csv', 'pdf']
            }
        ],
        //Code to add the colours to the data - temporary numbers have been added.

        "columnDefs": [
            {className: "dt-center", "targets": "_all"},
            {className: "maxpx300", "targets": [1]}, // Here - try and make this a maximum column width
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

                    if (!($th.text().includes('PW F') || $th.text().includes('DS F') || $th.text().includes('F Cov'))) {
                        if (!(isNaN(cellData))) { //if the value of the cell is a number then colour it.
                            // if (cellData==0.00){
                            //   cellData = MIN_VAL //Can't pass zero to the log so choose minimum value
                            // };
                            const colour = colorScale(cellData);
                            $(td).css('background-color', colour)
                        }
                    }
                    // Format the column numbers
                    //Ignore for the peak ID
                    if ($th.text().includes('Pathway name')) {
                        $(td).addClass("text-centre")
                        $(td).addClass("maxpx300")
                    }
                    // If m_z or RT reformat the number to 2 dec places.
                    else if ($th.text().includes('PW F')) {
                        const value = $td.text()
                        const num = parseInt(value)
                        $td.empty();
                        $td.append(num);
                    } else if ($th.text().includes('DS F')) {
                        const value = $td.text()
                        const num = parseInt(value)
                        $td.empty();
                        $td.append(num);
                    } else if ($th.text().includes('F Cov')) {
                        const value = $td.text()
                        const num = parseFloat(value).toFixed(1)
                        $td.empty();
                        $td.append(num);
                        $td.append(' %');

                    }

                    // If the number is some of the tissue data
                    else {
                        const value = $td.text()
                        if (value > 0) {
                            const num = parseFloat(value).toExponential(1)
                            $td.empty();
                            $td.append(num);
                            $(td).addClass("data");
                        } else {
                            $(td).addClass("NotDetected");
                        }

                    }
                }
            },

            {
                targets: [0], // Hide the reactome ID but we still might want to use it
                "visible": false
            },
        ],
        // Add the tooltips to the dataTable header
        "initComplete": function (settings) {

            $(".col").each(function () {
                let $td = $(this);
                let header = $td.text().trim();
                let head_split = header.split(" ");
                let string = "";
                let ls = "";
                if (header == "Pathway name")
                    string = '';
                else if (header == "PW F")
                    string = "No. unique formulae found in the pathway";
                else if (header == "DS F")
                    string = "No. unique formulae from the pathway found in the dataset";
                else if (header == "F Cov")
                    string = "Pathway formula coverage in dataset";
                else {
                    string = `Changes in ${head_split[0]} tissue from`;
                    const header_words = head_split.length;
                    const ls_check = header_words - 1;
                    ls = get_lifestage(head_split[ls_check]);
                    string = `${string} ${ls} compared to Whole ${ls} flies`;
                }

                //Change the title attribute of the column to the string/tooltip info
                // console.log("This is the string ", string)
                $td.attr({title: `${string}`});
                $td.attr('data-toggle', "tooltip");
                $td.attr('data-placement', "top");
            });

            enableTooltips();
        },
    })

//Return the table so that the it is resuable.

    let t1 = performance.now();
    console.log("Time to initialise the table " + (t1 - t0) + " milliseconds.")
    console.log("returning table")
    return table;
}

function get_lifestage(ls_string) {
    let ls = "";
    if (ls_string == "(F)")
        ls = "Females";
    else if (ls_string == "(M)")
        ls = "Males";
    else if (ls_string == "(L)")
        ls = "Larvae";

    return ls
}

//Update the metabolite side panel depending on which row is selected.
//Let tissue name = the first text sent back from the row (more or less)
function updatePathwaySidePanel(obj, data_url, met_ex_url, pwy_url) {

    let currentRow = $(obj).closest("tr");
    let reactome_id = $(`#${data_url}`).DataTable().row(currentRow).data()[0];
    let pathway_name = $(`#${data_url}`).DataTable().row(currentRow).data()[1];

    console.log("updating for pathway", reactome_id, pathway_name)
    console.log("pathway met url", pwy_url)


    const handleUpdate = function (returned_data) {
        updatePathwayInfo(returned_data, pathway_name, met_ex_url)
        updateReactomePathway(reactome_id, pathway_name)

    };
    //Update the bottom panel with a diagram using the Reactome ID.

    const url = `/met_explore/metabolite_pathway_data/${reactome_id}`
    fetch(url)
        .then(res => res.json())//response type
        .then(handleUpdate);

    // find all the paragraphs with id peak in the side panel
    $("fieldset[id='click_info']").hide();
    $("fieldset[class^='pathway_details']").show();
    $("p[id^='pwy_id']").html(`<a href="${pwy_url}?${pwy_url}=${pathway_name}" data-toggle="tooltip"
  title="FlyMet metabolites and peaks found in ${pathway_name}" target="_blank">${pathway_name} in FlyMet</a>`);

    enableTooltips();
}

//Enable tooltips as a reusable function as most are made dynamically.
function enableTooltips() {
    $('[data-toggle="tooltip"]').tooltip({
        container: 'body'
    });
}

// Update the compound names and any details for the side panel.
function updatePathwayInfo(returned_data, pathway_name, met_ex_url) {
    let cmpd_details = returned_data.cmpd_details
    let cmpds = Object.keys(cmpd_details)
    let no_cmpds = cmpds.length;

    let sideDiv = document.getElementById("dataDiv");
    sideDiv.innerHTML = "";

    let headerDiv = document.createElement('div');
    headerDiv.setAttribute('class', 'sidebar p-2');
    let cmpd_list = cmpds.toString()

    //Set the header with a link to all metabolites in the cmpd_list
    let url_pwm = `${met_ex_url}${cmpd_list}`; //pathway metabolites

    let met_tooltip = `data-toggle="tooltip" title="${pathway_name} metabolites found in Flymet"`

    let metabolite_header = `<a href="${url_pwm}"${met_tooltip} target=_"blank">Metabolites in FlyMet`;
    headerDiv.innerHTML = metabolite_header;
    sideDiv.appendChild(headerDiv);

    enableTooltips()

    //List all the metabolites in the pathway individually.
    for (var i = 0; i < no_cmpds; i++) {

        let cmpdDiv = document.createElement('div');
        cmpdDiv.setAttribute('class', 'p-2 small');

        let url_cmpd = `${met_ex_url}${cmpds[i]}`;
        let name = cmpd_details[cmpds[i]].name
        let formula = cmpd_details[cmpds[i]].formula
        let chebi_id = cmpd_details[cmpds[i]].chebi_id
        let r_chebi = cmpd_details[cmpds[i]].related_chebi
        let related_chebi

        if (r_chebi != null) {
            related_chebi = `or ${r_chebi}`
        } else {
            related_chebi = ''
        }

        let cmpd_info = `<div><span><a href="${url_cmpd}" target = _"blank">${name} (ChEBI: ${chebi_id} ${related_chebi}; formula: ${formula})</a></span></div>`
        cmpdDiv.innerHTML = cmpd_info;
        sideDiv.appendChild(cmpdDiv);

    }
}


function updateReactomePathway(pathway_id, pathway_name) {

    console.log("In the reactome update ", pathway_id)
    console.log("reactome_token ", reactome_token)


    let dTitleDiv = document.getElementById("diagramTitle"); //diagram_title_div
    dTitleDiv.innerHTML = "";
    //
    let pwyDiv = document.createElement(`p`);
    let pwy_tooltip = `data-toggle="tooltip" title="${pathway_name} in Reactome"`

    let pwy_info = `<a href="https://reactome.org/content/detail/${pathway_id}" ${pwy_tooltip} target="_blank">${pathway_name}: Reactome</a>`;
    pwyDiv.innerHTML = pwy_info
    dTitleDiv.appendChild(pwyDiv);

    var diagram = Reactome.Diagram.create({
        "placeHolder": "diagramHolder",
        // "width": 1000,
        // "height": 500
    });

    diagram.loadDiagram(pathway_id);
    // diagram.highlightItem('')
    diagram.onDiagramLoaded(function (loaded) {
        console.info("Loaded ", loaded);

    });

    diagram.setAnalysisToken(reactome_token, 'TOTAL')

    //This allows exansion of the Reactome Diagram to the page using width_100
    let diagram_holder = document.getElementsByClassName("pwp-DiagramVisualiser")
    let diagram_holder2 = document.getElementsByClassName("pwp-ViewerContainer")

    var i;
    for (i = 0; i < diagram_holder.length; i++) {
        diagram_holder[i].setAttribute('class', "pwp-DiagramVisualiser width_100");
        diagram_holder2[i].setAttribute('class', "pwp-ViewerContainer pwp-DiagramViewer width_100")

    }

    $("#diagram_info").show();
    enableTooltips();
}

export
{
    initialise_pwy_table, initialise_pals_table, updatePathwaySidePanel
}
