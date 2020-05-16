require('./init_datatables.js');
const d3 = require('d3');
require('bootstrap/js/dist/tooltip');


function initialise_pals_table(tableName, lowpoint, midpoint, highpoint){
    let t0 = performance.now();
    const tName = '#'+tableName;
    console.log("tablename", tName)
    const MIN_VAL = 3000;
    const pals_data = document.getElementById('pals_data').getAttribute('url');

    let table = $(tName).DataTable({

        "scrollY": "100vh",
        "scrollCollapse": true,
        scrollX: true,
        fixedheader: true,
        colReorder: true,
        ajax: {
          url: "/met_explore/pals_data",
          cache: true,  //This is so we can use the cached data otherwise DT doesn't allow it.
        },

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
            {className: "maxpx300", "targets": [1] }, // Here - try and make this a maximum column width
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
                    if ($th.text().includes('Pathway name')){
                      $(td).addClass("text-centre")
                      $(td).addClass("maxpx300")
                    }
                    // If m_z or RT reformat the number to 2 dec places.
                   else if ($th.text().includes('PW F')){
                      const value = $td.text()
                      const num = parseInt(value)
                      $td.empty();
                      $td.append(num);
                    }
                    else if ($th.text().includes('DS F')){
                      const value = $td.text()
                      const num = parseInt(value)
                      $td.empty();
                      $td.append(num);
                    }

                    else if ($th.text().includes('F Cov')){
                      const value = $td.text()
                      const num = parseFloat(value).toFixed(1)
                      $td.empty();
                      $td.append(num);
                      $td.append(' %');

                    }

                    // If the number is some of the tissue data
                    else {
                      const value = $td.text()
                      if (value > 0){
                      const num = parseFloat(value).toExponential(1)
                      $td.empty();
                      $td.append(num);
                      $(td).addClass("data");
                    } else {$(td).addClass("NotDetected");}

                    }
                    }
                  },

                  {
                    targets:[0], // Hide the reactome ID but we still might want to use it
                    "visible": false
                  },
        ],
        // Add the tooltips to the dataTable header
        "initComplete": function(settings){

                    $(".col").each(function(){
                      let $td = $(this);
                      let header = $td.text().trim();
                      let head_split = header.split(" ");
                      let string ="";
                      let ls="";
                      if (header=="Pathway name")
                        string = '';
                      else if (header=="PW F")
                        string = "No. unique formulae found in the pathway";
                      else if (header=="DS F")
                        string ="No. unique formulae from the pathway found in the dataset";
                      else if (header=="F Cov")
                        string ="Pathway formula coverage in dataset";
                      else {
                        string =`Changes in ${head_split[0]} tissue from`;
                        const header_words = head_split.length;
                        const ls_check = header_words-1;
                        ls = get_lifestage(head_split[ls_check]);
                        string=`${string} ${ls} compared to Whole ${ls} flies`;}

                      //Change the title attribute of the column to the string/tooltip info
                      // console.log("This is the string ", string)
                      $td.attr({title: `${string}`});
                      $td.attr('data-toggle', "tooltip");
                      $td.attr('data-placement', "top" );
                  });
                  /* Apply the tooltips */
                  $('[data-toggle="tooltip"]').tooltip({
                      container: 'body'
                  });
              },
    })

    // add data here

//Return the table so that the it is resuable.

    let t1 = performance.now();
    console.log("Time to initialise the table " + (t1 - t0) + " milliseconds.")
    console.log("returning table")
    return table;
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
//Update the metabolite side panel depending on which row is selected.
//Let tissue name = the first text sent back from the row (more or less)
function updatePathwaySidePanel(obj){

  let currentRow = $(obj).closest("tr");
  let reactome_id = $('#pals_data').DataTable().row(currentRow).data()[0];
  let pathway_name = $('#pals_data').DataTable().row(currentRow).data()[1];

  console.log("updating for pathway", reactome_id, pathway_name)


  const handleUpdate = function(returned_data) {
    updatePathwayInfo(returned_data)

};

const url = `/met_explore/metabolite_pathway_data/${reactome_id}`
fetch(url)
.then(res => res.json())//response type
.then(handleUpdate);

// find all the paragraphs with id peak in the side panel
$("fieldset[id='click_info']").hide();
$("fieldset[class^='pathway_details']").show();
$("p[id^='pwy_id']").text(`${pathway_name}`);

}

// Update the compound names and any details for the side panel.
function updatePathwayInfo(returned_data){
  let cmpd_details = returned_data.cmpd_details
  let cmpds = Object.keys(cmpd_details)
  let no_cmpds = cmpds.length;

  let sideDiv =  document.getElementById("dataDiv");
  sideDiv.innerHTML = "";

  let headerDiv = document.createElement('div');
  headerDiv.setAttribute('class', 'sidebar p-2');
  cmpd_list = cmpds.toString()

  //Set the header with a link to all metabolites in the cmpd_list
  let url_pwm = `met_ex_all/${cmpd_list}`; //pathway metabolites
  let metabolite_header = `<a href="${url_pwm}">Metabolites</a>`;
  headerDiv.innerHTML =  metabolite_header;
  sideDiv.appendChild(headerDiv);

  //List all the metabolites in the pathway individually.
  for (var i = 0; i < no_cmpds; i++) {

      let cmpdDiv = document.createElement('div');
      cmpdDiv.setAttribute('class', 'p-2 small');

      let url_cmpd = `met_ex_all/${cmpds[i]}`;
      let name = cmpd_details[cmpds[i]].name
      let formula = cmpd_details[cmpds[i]].formula

       let cmpd_info = `<div><span><a href="${url_cmpd}">${name} (${formula})</span></div>`
            cmpdDiv.innerHTML =  cmpd_info;
            sideDiv.appendChild(cmpdDiv);

}
}


$(document).ready(function() {
    $("fieldset[class^='pathway_details']").hide();
  console.log ("min, mean, max values for table ", min_value, mean_value, max_value)
  let pals_table = initialise_pals_table("pals_data", min_value, mean_value, max_value);

      pals_table.on( 'click', 'tr', function () {
        updatePathwaySidePanel(this);
      } );
});