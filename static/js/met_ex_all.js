require('./init_datatables.js');
const d3 = require('d3');
require('bootstrap/js/dist/tooltip');

function initialise_met_table(tableName){
    const tName = '#'+tableName;
    console.log("tablename ", tName)
    // const peak_data = document.getElementById('peak_list').getAttribute('url');

    // console.log("Peak data ", peak_data)


  //   const DBLinks = [
  //     "https://www.ebi.ac.uk/chebi/searchId.do?chebiId=",
  // "http://www.yahoo.com" ,
  // "http://www.google.com",
  //   "http://www.duckduckgo.com"
  //   ];

    let table = $(tName).DataTable({

        "scrollY": "100vh",
        "scrollCollapse": true,
        "scrollX": true,
        fixedheader: true,
        colReorder: true,
        ajax: {
          url: "/met_explore/metabolite_data",
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
                    // console.log($td.text())
                    // let $th = $(".col").eq($td.index());

                    // const colorScale = d3.scaleLog()
                    //     .domain([MIN_VAL, midpoint, highpoint])
                    //     .range(["#1184fc", "#D6DCE6", "#8e3b3d"]);

                    //If the column header doesn't include the string Tissue then colour the column.
                    // Format the column numbers
                    //Ignore for the peak ID
                   //  if ($th.text().includes('Peak ID')){
                   //    $(td).addClass('"text-center"')
                   //  }
                   //  // If m_z or RT reformat the number to 2 dec places.
                   // else if ($th.text().includes('RT')){
                   //    const value = $td.text()
                   //    const num = parseFloat(value).toFixed(2)
                   //    $td.empty();
                   //    $td.append(num);
                   //  }
                   //  else if ($th.text().includes('m/z')){
                   //    const value = $td.text()
                   //    const num = parseFloat(value).toFixed(4)
                   //    $td.empty();
                   //    $td.append(num);
                   //  }

                    // If the number is some of the tissue data
                    // else {
                    //   const value = $td.text()
                    //   if (value > 0){
                    //   const num = parseFloat(value).toExponential(2)
                    //   $td.empty();
                    //   $td.append(num);
                    //   $(td).addClass("data");
                    // } else {$(td).addClass("NotDetected");}
                    //
                    // }
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
        // Add the tooltips to the dataTable header
        // "initComplete": function(settings){
        //
        //             $(".col").each(function(){
        //
        //               let $td = $(this);
        //               let header = $td.text();
        //               let head_split = header.split(" ");
        //               let string ="";
        //               let ls="";
        //
        //               if (head_split[0]=="m/z")
        //                 string = "mass-to-charge ratio";
        //               else if (head_split[0]=="Peak")
        //                 string ="";
        //               else if (head_split[0]=="RT")
        //                 string ="Retention Time";
        //               else
        //                 string =`${head_split[0]} tissue from`;
        //                 const header_words = head_split.length;
        //                 const ls_check = header_words-1;
        //                 ls = get_lifestage(head_split[ls_check])
        //
        //               //Change the title attribute of the column to the string/tooltip info
        //               $td.attr({title: `${string} ${ls}`});
        //               $td.attr('data-toggle', "tooltip");
        //               $td.attr('data-placement', "top" );
        //           });
        //           /* Apply the tooltips */
        //           $('[data-toggle="tooltip"]').tooltip({
        //               container: 'body'
        //           });
        //       },
    })

    // add data here

//Return the table so that the it is resuable.
    //
    // let t1 = performance.now();
    // console.log("Time to initialise the table " + (t1 - t0) + " milliseconds.")
    // console.log("returning table")
    return table;
}


// function get_lifestage(ls_string){
//
//   let ls = "";
//   if (ls_string=="(F)")
//     ls ="Females";
//   else if (ls_string=="(M)")
//       ls ="Males";
//   else if (ls_string=="(L)")
//         ls ="Larvae";
//
//   return ls
// }
//Update the metabolite side panel depending on which row is selected.
//Let tissue name = the first text sent back from the row (more or less)
function updateMetboliteSidePanel(obj){

  var currentRow = $(obj).closest("tr");
  var cmpd_id = $('#metabolite_list').DataTable().row(currentRow).data()[0];
  let cmpd_name = $(obj).children().first().text();

  console.log("updating for cmpd", cmpd_name)
  console.log("with a cmpd_id", cmpd_id)

  const handleUpdate = function(returned_data) {
  //
    let radio_filter = document.getElementById('filtered')
    let radio_all = document.getElementById('all_adducts')
    let radio_all_check = radio_all.checked
    // radio_all_check should start off false

  // Update the peak table
  console.log("handling update")
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
  console.log("Updating adducts")
  let radio_all = document.getElementById('all_adducts');
  let radio_all_check = radio_all.checked
  updatePeakData(returned_data, radio_all_check);
 }

// Update the compound names and any details we want on the side panel
function updatePeakData(returned_data, radio_all_check, cmpd_name){

  console.log("in update peak data")

  const peak_groups = returned_data.peak_groups;
  const columns = returned_data.columns

  let sideDiv =  document.getElementById("dataDiv");
  sideDiv.innerHTML = "";

  no_groups = peak_groups.length
  let peak_group_no = 0;

  // For each peak group
  for (var i = 0; i < no_groups; i++) {

      let groupDiv = document.createElement('div');
      groupDiv.setAttribute('class', 'p-2');
      let peak_group = peak_groups[i];
      let items_in_gp = peak_group.length;

      // If any of the adducts in the group are M+H or M-H have a flag
      let m_adduct = false;
      for (var j = 0; j < items_in_gp; j++){
        this_peak = peak_group[j]
        if (this_peak['adduct']=='M+H' || this_peak['adduct']=='M+H'){
          m_adduct =true;
        }
      }
    // If the radio check is all or the group contains an M+H or M-H adduct add the peak group table
      if (radio_all_check || m_adduct){

        console.log("peak_gp", peak_group)

        peak_group_no = peak_group_no+1;
        let group_header = `<p class= "sidebar">Peak Group: ${peak_group_no}</p>
        <hr class="my-3">`
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


  let group_table = `<div class="p-2 pb-0 table-responsive">
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
          let ion = this_group['adduct'];
          let nm1 = Number(this_group['nm']);
          let nm = nm1.toFixed(4);
          let rt1 = Number(this_group['rt']);
          let rt =  rt1.toFixed(2);

          let no_other_cmpds = this_group['no_adducts']-1 //Remove one for this compound.
          let conf =  this_group['conf']

          console.log("HERE", no_other_cmpds, conf)

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


          group_table = group_table +`<tr><td class="badge badge-pill badge-${success}">${badge_info}</td><td>${peak_id}</td>`
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
