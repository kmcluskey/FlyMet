require('./init_datatables.js');
const d3 = require('d3');
require('bootstrap/js/dist/tooltip');

function initialise_met_table(tableName){
    const tName = '#'+tableName;
    console.log("tablename ", tName)

    let table = $(tName).DataTable({

        "scrollY": "100vh",
        "scrollCollapse": true,
        "scrollX": true,
        fixedheader: true,
        colReorder: true,
        ajax: {
          url: `/met_explore/metabolite_data/${cmpd_list}`,
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
            {

                "targets": '_all',
                "createdCell": function (td, cellData, rowData, row, col) {

                    let $td = $(td);

                    }
                  },

                  {
                    targets: 'cmpd_id',
                    "searchable": false,
                    "visible": false

                  },

                  {
                    targets: 'DB',
                    // This renders the column with the class DB i.e. DB identifiers.
                    "render": function (data, type, full, meta ) {
                    // //
                    let link =""
                    let linker =", "
                    let str_array = data.split(",");
                    // For each database identifier
                    for (let i=0; i < str_array.length; i++){
                      let cell_data = "";
                      if (i==(str_array.length)-1) { //If it's the last item in the list
                        linker = ""
                        }

                      cell_data = str_array[i].trim() // Remove the white spaces from the DB references
                      if (cell_data.startsWith('CHEBI')){
                        link = link+'<a href=https://www.ebi.ac.uk/chebi/searchId.do?chebiId='+cell_data+'>'+cell_data+'</a>'+linker
                      }
                      else if (cell_data.startsWith('HMDB')){
                        link = link+'<a href=http://www.hmdb.ca/metabolites/'+cell_data+'>'+cell_data+'</a>'+linker
                      }
                      else if (cell_data.startsWith('C')){
                        link = link+'<a href=https://www.genome.jp/dbget-bin/www_bget?cpd:'+cell_data+'>'+cell_data+'</a>'+linker
                      }
                      else if (cell_data.startsWith('LM')){
                        link = link+'<a href=http://www.lipidmaps.org/data/LMSDRecord.php?LMID='+cell_data+'>'+cell_data+'</a>'+linker
                      }
                      }
                      return link;
                      }
                    }
        ],
})
    return table;
}

//Update the metabolite side panel depending on which row is selected.
//Let tissue name = the first text sent back from the row (more or less)
function updateMetboliteSidePanel(obj){

  var currentRow = $(obj).closest("tr");
  var cmpd_id = $('#metabolite_list').DataTable().row(currentRow).data()[0];
  let cmpd_name = $(obj).children().first().text();

  const handleUpdate = function(returned_data) {
  //
    let radio_filter = document.getElementById('filtered')
    let radio_all = document.getElementById('all_adducts')
    let radio_all_check = radio_all.checked
    // radio_all_check should start off false

  // Update the peak table
  updatePeakData(returned_data, radio_all_check, cmpd_name)
  //
    // Redraw the adduct data is the radio button is clicked.
    $("input[name='radio_adducts']" ).click(function(){
      {updateAdducts(returned_data, cmpd_name)};
      });
};




const url = `/met_explore/metabolite_peak_data/${cmpd_id}`
fetch(url)
.then(res => res.json())//response type
.then(handleUpdate);

//display all the peaks that are annotated to a particular compound
$("fieldset[id='click_info']").hide();
$("fieldset[class^='peak_details']").show();
$("p[id^='compound_id']").text('Peak groups annotated as ' + cmpd_name);

}



function updateAdducts(returned_data, cmpd_name){
//
  let radio_all = document.getElementById('all_adducts');
  let radio_all_check = radio_all.checked
  updatePeakData(returned_data, radio_all_check);
 }

// Update the compound names and any details we want on the side panel
function updatePeakData(returned_data, radio_all_check, cmpd_name){

  console.log("Updating peak data")

  const peak_groups = returned_data.peak_groups;
  const columns = returned_data.columns

  let sideDiv =  document.getElementById("dataDiv");
  sideDiv.innerHTML = "";

  no_groups = peak_groups.length
  let peak_group_no = 0;

  // For each peak group
  for (var i = 0; i < no_groups; i++) {

      let groupDiv = document.createElement('div');
      groupDiv.setAttribute('class', 'p-1');
      let peak_group = peak_groups[i];
      let items_in_gp = peak_group.length;

      // If any of the adducts in the group are M+H or M-H have a flag
      let m_adduct = false;
      for (var j = 0; j < items_in_gp; j++){
        this_peak = peak_group[j]
        if (this_peak['adduct']=='M+H' || this_peak['adduct']=='M-H' || this_peak['adduct']=='M'){
          m_adduct =true;
        }
      }
    // If the radio check is all or the group contains an M+H or M-H adduct add the peak group table
      if (radio_all_check || m_adduct){

        let peak_ids =""
        for (var p = 0; p < items_in_gp; p++){
          this_peak = peak_group[p];
          console.log("this_peak_id ", this_peak['peak_id'] )
          peak_ids = peak_ids+this_peak['peak_id']+",";
        }

        let peak_list = peak_ids.substring(0,peak_ids.length-1) //remove last "," from string the lazy way
        peak_group_no = peak_group_no+1;
        var url_pg = `peak_explorer/${peak_list}`
        let group_header = `<hr class="my-2"><p class= "sidebar"><a href="${url_pg}">Peak Group: ${peak_group_no}</a></p>`
        group_table = get_peak_gp_table(columns, peak_group, cmpd_name);
        group = group_header+group_table;
        groupDiv.innerHTML =  group;
        sideDiv.appendChild(groupDiv);
      }

      //Add the tooltips after all divs created.
      add_side_tooltips()
    }
}

// Returns a single HTML table for a single peak group
function get_peak_gp_table(columns, peak_group, cmpd_name){


  let group_table = `<div class="pl-2 pb-0 table-responsive">
      <table class="table table-sm table-bordered side_table">
      <thead>
        <tr>`

      // Add Table headers from column names
      for (var i = 0; i < columns.length; i++) {
        head = `<th class=${columns[i]}>${columns[i]}</th>`
        group_table = group_table+head
      }

        group_table = group_table+`<thead>
        <tr> <tbody>`

        let peaks_in_gp = peak_group.length;
        for (var i = 0; i < peaks_in_gp; i++) {
          this_group=peak_group[i];
          let peak_id = this_group['peak_id'];
          let peak_url = `peak_explorer/${peak_id}`

          let ion = this_group['adduct'];
          let nm1 = Number(this_group['nm']);
          let nm = nm1.toFixed(4);
          let rt1 = Number(this_group['rt']);
          let rt =  rt1.toFixed(2);

          let no_other_cmpds = this_group['no_adducts']-1 //Remove one for this compound.
          let conf =  this_group['conf']

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


          group_table = group_table +`<tr><td class="badge badge-pill badge-${success}">${badge_info}</td><td><a href="${peak_url}">${peak_id}<a></td>`
          data_list=[ion, nm, rt]
          // group_table = group_table+`<tr>`
          for (var d = 0; d < data_list.length; d++) {
            group_table = group_table+`<td>${data_list[d]}</td>`
          }
          group_table = group_table+`</tr>`
 }
  return group_table

};
// Add table header tooltips --these are temporary.
//KMCL: These tool tips have to be replaced with something responsive - i.e. where the buttons change depending on the data.
function add_side_tooltips(){

  $('.I').tooltip({title: `This peak has been Identified using a library standard`, placement: "top"});
  $('.F').tooltip({title: `MS/MS Fragmentation data has been used to identify this peak`, placement: "top"});
  $('.A').tooltip({title: `This peak also annotates X other compounds`, placement: "top"});
  $('.Conf').tooltip({title: `The confidence level given to this annotation (see Key)`, placement: "top"});
  $('.Ion').tooltip({title: `The ion species`, placement: "top"});
  $('.Mass').tooltip({title: `The neutral mass of the compound associated with this annotation`, placement: "top"});
  $('.RT').tooltip({title: `The retention time of the compound`, placement: "top"});

};


$(document).ready(function() {

  $("fieldset[class^='peak_details']").hide();

  let metabolite_table = initialise_met_table("metabolite_list");

      metabolite_table.on( 'click', 'tr', function () {
      updateMetboliteSidePanel(this);
      } );

});
