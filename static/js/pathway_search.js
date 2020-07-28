require('./init_datatables')
require('bootstrap/js/dist/tooltip');
const d3 = require('d3');

Awesomplete = require('awesomplete');
require('awesomplete/awesomplete.css');
require('../css/awesomechanges.css')

function initialise_pcompare_table(tableName, lowpoint, midpoint, highpoint){
    // let t0 = performance.now();
    const tName = '#'+tableName;
    let table = $(tName).DataTable({

      drawCallback: function(settings){
          /* Add some tooltips for demonstration purposes */
          $('.NotDetected2').tooltip({title: "This MS peak was not detected for this tissue/life stage combination", placement: "top", position:"relative"})
      },

        // responsive: true,
        "scrollY": "100vh",
        "scrollCollapse": true,
        "scrollX": true,
        fixedheader: true,
        colReorder: true,
        select: {
            style: 'single'
        },
        //code to override bootstrap and keep buttons on one line.
        dom: "<'row'<'col-sm-3'l><'col-sm-4'B><'col-sm-3'f>>" +
        "<'row'<'col-sm-12'rt>>" +
        "<'row'<'col-sm-6'i><'col-sm-6'p>>",
        buttons: [ 'copy',

        {
            extend: 'colvis',
            columns: ':gt(0)' //do not include first column in list of columns to remove
        },

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
                        $(td).addClass("NotDetected2");
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

//Update the metabolite side panel depending on which row is selected.
//Let tissue name = the first text sent back from the row (more or less)
// KMCL*** This code is copied directly from the peak_explorer - can this be made reusable??
//---------------------------------------------------------------------------------------
function updatePeakSidePanel(obj){
  let peak_id = $(obj).children().first().text();

  console.log("updating for peak", peak_id)


  const handleUpdate = function(returned_data) {

    let radio_filter = document.getElementById('filtered')
    let radio_all = document.getElementById('all_adducts')
    let radio_all_check = radio_all.checked

    // Update the peak table
    updatePeakData(returned_data, radio_all_check)

    // Redraw the adduct data if the radio button is clicked.
    $("input[name='radio_adducts']" ).click(function(){
      {updateAdducts(returned_data)};
    });

};

const url = `/met_explore/peak_explore_annotation_data/${peak_id}`
fetch(url)
.then(res => res.json())//response type
.then(handleUpdate);

// find all the paragraphs with id peak in the side panel
$("fieldset[id='click_info']").hide();
$("fieldset[class^='peak_details']").show();
$("p[id^='peak_id']").text('Peak ' + peak_id);

}

function updateAdducts(returned_data){

  console.log("Updating adducts")
  let radio_all = document.getElementById('all_adducts');
  let radio_all_check = radio_all.checked
  updatePeakData(returned_data, radio_all_check);
}


// Update the compound names and any details we want on the side panel
function updatePeakData(returned_data, radio_all_check){

  const cmpd_names = returned_data.cmpd_names;
  const adducts = returned_data.adducts;
  const conf_fact = returned_data.conf_fact;
  const neutral_mass = returned_data.neutral_mass;
  const no_other_cmpds = returned_data.no_other_cmpds;
  const cmpd_ids = returned_data.cmpd_ids

  let sideDiv =  document.getElementById("dataDiv");
  sideDiv.innerHTML = "";

  const no_cmpds = cmpd_names.length;
  let id_name ="";
  let frag_name="";
  let badge_info="";

  for (var i = 0; i < no_cmpds; i++) {
      const name = cmpd_names[i];
      const ion = adducts[i];
      const conf = conf_fact[i];
      const cmpd_id = cmpd_ids[i];

      var url_met = `met_ex_all/${cmpd_id}`
      var nm1 = Number(neutral_mass[i]);
      var nm = nm1.toFixed(4);

      let success ="";
      let identified="";
      if (conf == 4){
        identified ="I";
        badge_info="I"
        success="success";
        id_name=name;
      }
      else if (conf == 3){
        identified ="F";
        badge_info="F";
        success="warning";
        frag_name=name;
      }
      else if (conf == 0){
        identified ="A";
        badge_info =`A${no_other_cmpds}`;
        success="danger";
      }
        if (radio_all_check || ion=='M+H' || ion=='M-H'|| ion=='M'){ //draw if ion = M+H or M-H or if all adducts are chosen
        let peakDiv = document.createElement('div');
        peakDiv.setAttribute('class', 'p-2');

        let peak_info = `<span class="${identified} badge badge-pill badge-${success}">${badge_info}</span>
        <span id="cmpd_name" class="peak_data"><a href="${url_met}">${name}</a></span><div class="row pt-2">
        <div id ="Ion" class="col-sm-5 peak_data"><b>Ion: </b>${ion}</div>
        <div id ="NM" class="col-sm-7 peak_data"><b>Mass: </b>${nm}</div><br></div>`;
        peakDiv.innerHTML =  peak_info;
        sideDiv.appendChild(peakDiv);

      }
      add_side_tooltips(id_name, frag_name, no_other_cmpds); //Add the tooltips after all divs created.
    }
}

// Add table header tooltips --these are temporary.
//KMCL: These tool tips have to be replaced with something responsive - i.e. where the buttons change depending on the data.
function add_side_tooltips(id_name, frag_name, no_other_cmpds){
  $('.I').tooltip({title: `This MS peak has been Identified as ${id_name} using a library standard`, placement: "top"});
  $('.F').tooltip({title: `MS/MS Fragmentation data suggests that this peak is likely to be ${frag_name}`, placement: "top"});
  $('.A').tooltip({title: `This peak also annotates ${no_other_cmpds} other compounds`, placement: "top"});
};


//-----------------------------------------------------------------------------------



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
  $("fieldset[class^='peak_details']").hide();
  //Method to add an autocomplete search function to the DB
  loadData((url)).then(function(data) {
    new Awesomplete(pathway_search, {list: data.pathwayNames});
  });

  try {
    for (var i = 0; i < num_metabolites; i++) {

      let pwy_met_table = initialise_pcompare_table(`pwy_met_table_${i}`, min, mid, max);

      pwy_met_table.on( 'click', 'tr', function () {
        updatePeakSidePanel(this);
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

    //
    // Create ColVis on the first table only
    // let colvis = new $.fn.dataTable.ColVis(tables.table(0));
  //$( colvis.button() ).insertAfter('div.info');

  $('#DSF').tooltip({title: "Matching Formulae in found Flymet", placement: "top"});
  $('#PWF').tooltip({title: "Unique Formulae in the Pathway", placement: "top"});
  $('#Cov').tooltip({title: "Dataset/Pathway formulae coverage", placement: "top"});

  console.log('number of metabolites', num_metabolites)
  console.log('pathway passed', pathway_name);
  console.log('url', url)

});
