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


  // const handleUpdate = function(returned_data) {
  //
  //   let radio_filter = document.getElementById('filtered')
  //   let radio_all = document.getElementById('all_adducts')
  //   let radio_all_check = radio_all.checked
  //
  //   // Update the peak table
  //   updatePeakData(returned_data, radio_all_check)
  //
  //   // Redraw the adduct data is the radio button is clicked.
  //   $("input[name='radio_adducts']" ).click(function(){
  //     {updateAdducts(returned_data)};
  //   });

//};


// const url = `/met_explore/peak_explore_annotation_data/${peak_id}`
// fetch(url)
// .then(res => res.json())//response type
// .then(handleUpdate);

//display all the peaks that are annotated to a particular compound
$("fieldset[id='click_info']").hide();
$("fieldset[class^='peak_details']").show();
$("p[id^='compound_id']").text('This will show peaks for ' + cmpd_name +' with cmpd_id '+ cmpd_id);

}



// function updateAdducts(returned_data){
//
//   console.log("Updating adducts")
//   let radio_all = document.getElementById('all_adducts');
//   let radio_all_check = radio_all.checked
//   updatePeakData(returned_data, radio_all_check);
// }

// Update the compound names and any details we want on the side panel
// function updatePeakData(returned_data, radio_all_check){
//
//   const cmpd_names = returned_data.cmpd_names;
//   const adducts = returned_data.adducts;
//   const conf_fact = returned_data.conf_fact;
//   const neutral_mass = returned_data.neutral_mass;
//   const no_other_cmpds = returned_data.no_other_cmpds;
//
//   console.log(cmpd_names)
//
//   let sideDiv =  document.getElementById("dataDiv");
//   sideDiv.innerHTML = "";
//
//   const no_cmpds = cmpd_names.length;
//   let id_name ="";
//   let frag_name="";
//   let badge_info="";
//
//   for (var i = 0; i < no_cmpds; i++) {
//       const name = cmpd_names[i];
//       const ion = adducts[i];
//       const conf = conf_fact[i];
//
//       var nm1 = Number(neutral_mass[i]);
//       var nm = nm1.toFixed(4);
//
//       let success ="";
//       let identified="";
//       if (conf == 4){
//         identified ="I";
//         badge_info="I"
//         success="success";
//         id_name=name;
//       }
//       else if (conf == 3){
//         identified ="F";
//         badge_info="F";
//         success="warning";
//         frag_name=name;
//       }
//       else if (conf == 0){
//         identified ="A";
//         badge_info =`A${no_other_cmpds}`;
//         success="danger";
//       }
//
//         if (radio_all_check || ion=='M+H' || ion=='M-H'){
//         let peakDiv = document.createElement('div');
//         peakDiv.setAttribute('class', 'p-2');
//
//         let peak_info = `<span class="${identified} badge badge-pill badge-${success}">${badge_info}</span>
//         <span id="cmpd_name" class="peak_data">${name}</span><div class="row pt-2">
//         <div id ="Ion" class="col-sm-5 peak_data"><b>Ion: </b>${ion}</div>
//         <div id ="NM" class="col-sm-7 peak_data"><b>Mass: </b>${nm}</div><br></div>`;
//         console.log("here")
//         peakDiv.innerHTML =  peak_info;
//         sideDiv.appendChild(peakDiv);
//
//       }
//       add_side_tooltips(id_name, frag_name, no_other_cmpds); //Add the tooltips after all divs created.
//     }
// }
//
// // Add table header tooltips --these are temporary.
// //KMCL: These tool tips have to be replaced with something responsive - i.e. where the buttons change depending on the data.
// function add_side_tooltips(id_name, frag_name, no_other_cmpds){
//   $('.I').tooltip({title: `This MS peak has been Identified as ${id_name} using a library standard`, placement: "top"});
//   $('.F').tooltip({title: `MS/MS Fragmentation data suggests that this peak is likely to be ${frag_name}`, placement: "top"});
//   $('.A').tooltip({title: `This peak also annotates ${no_other_cmpds} other compounds`, placement: "top"});
// };
//
//
// function add_tooltips(obj){
//   console.log("adding tooltips")
//   $('.NotDetected').tooltip({title: "A MS peak was not detected for this tissue/life stage combination", placement: "top"})
//   $('.test').tooltip({title: "A MS peak was not detected for this tissue/life stage combination", placement: "top"})
//
// }

$(document).ready(function() {
  $("fieldset[class^='peak_details']").hide();

  let metabolite_table = initialise_met_table("metabolite_list");

      metabolite_table.on( 'click', 'tr', function () {
      updateMetboliteSidePanel(this);
      } );

});
