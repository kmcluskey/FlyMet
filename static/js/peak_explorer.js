require('./init_datatables.js');
const d3 = require('d3');
require('bootstrap/js/dist/tooltip');
import {initialise_table} from './flymet_tables';



function initialise_peak_table(tableName, lowpoint, midpoint, highpoint){
    const tName = '#'+tableName;
    console.log("tablename ", tName)
    const MIN_VAL = 3000;
    let table = $(tName).DataTable({
        // responsive: true,
        "scrollY": "100vh",
        "scrollCollapse": true,
        "scrollX": true,
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
            {
                "targets": '_all',
                "createdCell": function (td, cellData, rowData, row, col) {

                    let $td = $(td);
                    let $th = $td.closest('table').find('th').eq($td.index());

                    const colorScale = d3.scaleLog()
                        .domain([MIN_VAL, midpoint, highpoint])
                        .range(["#1184fc", "#D6DCE6", "#8e3b3d"]);

                    // If the column header doesn't include the string Tissue then colour the column.

                    if (!($th.text().includes('Peak ID') || $th.text().includes('m/z') || $th.text().includes('RT'))) {
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
    })

//Return the table so that the it is resuable.
    console.log("returning table")
    return table;
}

//Update the metabolite side panel depending on which row is selected.
//Let tissue name = the first text sent back from the row (more or less)
function updatePeakSidePanel(obj){
  let peak_id = $(obj).children().first().text();

  console.log("updating for peak", peak_id)


  const handleUpdate = function(returned_data) {

    let radio_filter = document.getElementById('filtered')
    let radio_all = document.getElementById('all_adducts')
    let radio_all_check = radio_all.checked

    // Update the peak table
    updatePeakData(returned_data, radio_all_check)

    // Redraw the adduct data is the radio button is clicked.
    $("input[name='radio_adducts']" ).click(function(){
      {updateAdducts(returned_data)};
    });

};

function updateAdducts(returned_data){

  console.log("Updating adducts")
  let radio_all = document.getElementById('all_adducts');
  let radio_all_check = radio_all.checked
  updatePeakData(returned_data, radio_all_check);
}

const url = `/met_explore/peak_explore_annotation_data/${peak_id}`
fetch(url)
.then(res => res.json())//response type
.then(handleUpdate);

// find all the paragraphs with id peak in the side panel
$("fieldset[id='click_info']").hide();
$("fieldset[class^='peak_details']").show();
$("p[id^='peak_id']").text('Peak ' + peak_id);

}

// Update the compound names and any details we want on the side panel
function updatePeakData(returned_data, radio_all_check){

  const cmpd_names = returned_data.cmpd_names;
  const adducts = returned_data.adducts;
  const conf_fact = returned_data.conf_fact;
  const neutral_mass = returned_data.neutral_mass;
  const no_other_cmpds = returned_data.no_other_cmpds;

  console.log(cmpd_names)

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

      var nm1 = Number(neutral_mass[i]);
      var nm = nm1.toFixed(2);

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
      }
      else if (conf == 0){
        identified ="A";
        badge_info =`A${no_other_cmpds}`;
        success="danger";
      }

        if (radio_all_check || ion=='M+H' || ion=='M-H'){
        let peakDiv = document.createElement('div');
        peakDiv.setAttribute('class', 'p-2');

        let peak_info = `<span class="${identified} badge badge-pill badge-${success}">${badge_info}</span>
        <span id="cmpd_name" class="peak_data">${name}</span><div class="row pt-2">
        <div id ="Ion" class="col-sm-5 peak_data"><b>Ion: </b>${ion}</div>
        <div id ="NM" class="col-sm-7 peak_data"><b>Mass: </b>${nm}</div><br></div>`;
        console.log("here")
        add_side_tooltips(id_name, frag_name, no_other_cmpds);
        peakDiv.innerHTML =  peak_info;
        sideDiv.appendChild(peakDiv);

      }
    }
}

// Add table header tooltips --these are temporary.
//KMCL: These tool tips have to be replaced with something responsive - i.e. where the buttons change depending on the data.
function add_side_tooltips(id_name, frag_name, no_other_cmpds){
  $('.I').tooltip({title: `This MS peak has been Identified as ${id_name} using a library standard`, placement: "top"});
  $('.F').tooltip({title: `MS/MS Fragmentation data suggests that this peak is likely to be ${frag_name}`, placement: "top"});
  $('.A').tooltip({title: `This peak also annotates ${no_other_cmpds} other compounds`, placement: "top"});
};


function add_tooltips(obj){
  $('.NotDetected').tooltip({title: "A MS peak was not detected for this tissue/life stage combination", placement: "top"})

}

$(document).ready(function() {
    $("fieldset[class^='peak_details']").hide();

    let peak_table = initialise_peak_table("peak_list", min_value, mean_value, max_value);
    add_tooltips(peak_table);

    peak_table.on( 'click', 'tr', function () {
      updatePeakSidePanel(this);
    } )

});
