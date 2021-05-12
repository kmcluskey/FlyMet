require('./init_datatables.js');
const d3 = require('d3');
require('bootstrap/js/dist/tooltip');

// Enable tooltips as a reusable function as most are made dynamically.
function enableTooltips(){
  $('[data-toggle="tooltip"]').tooltip({
      container: 'body'
  });
}

function initialise_gene_table(tableName){
    const tName = '#'+tableName;
    console.log("tablename ", tName)

    let table = $(tName).DataTable({

        "scrollY": "100vh",
        "scrollCollapse": true,
        "scrollX": true,
        fixedheader: true,
        colReorder: true,
        ajax: {
          url: `/met_explore/gene_data/${gene_list}`,
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
                "columnDefs": [
                    {className: "dt-center", "targets":"_all"},
                    {

                        "targets": '_all',
                        "createdCell": function (td, cellData, rowData, row, col) {
                          let $td = $(td);

                            }
                          },
                          {
                            "targets": 'FlyBaseID',
                            "render": function (data, type, row, meta ) {
                              return '<a href=http://flybase.org/reports/'+data+' target=_blank>'+data+'</a>';
                            }
                            },
                            {
                              "targets": 'Annotation',
                              "render": function (data, type, row, meta ) {
                                return '<a href=http://flyatlas.gla.ac.uk/FlyAtlas2/index.html?search=gene&gene='+data+'&idtype=cgnum target=_blank>'+data+'</a>';
                              }
                          },
                ],

                // Add the tooltips to the dataTable header
                "initComplete": function(settings){
                            $(".col").each(function(){
                              let $td = $(this);
                              let header = $td.text().trim();
                              // let head_split = header.split(" ");
                              let string ="";
                              // let ls="";
                              if (header=="FlyBaseID")
                                string = "Link to gene information in FlyBase";
                              else if (header=="FlyAtlas2 link")
                                string = "Annotation link to gene expression in FlyAtlas 2";

                              //Change the title attribute of the column to the string/tooltip info
                              // console.log("This is the string ", string)
                              $td.attr({title: `${string}`});
                              $td.attr('data-toggle', "tooltip");
                              $td.attr('data-placement', "top" );
                          });
                          enableTooltips();
                      },
        })
            return table;
        }

//Update the multi_omics side panel depending on which row is selected.
function updateGeneSidePanel(obj){

  var currentRow = $(obj).closest("tr");
  var gene_id = $('#gene_list').DataTable().row(currentRow).data()[0];

  console.log("updating for cmpd", gene_id)
  const handleUpdate = function(returned_data) {
    updateOmicsData(returned_data)
};

const url = `/met_explore/gene_omics_data/${gene_id}`
fetch(url)
.then(res => res.json())//response type
.then(handleUpdate);

//display all the peaks that are annotated to a particular compound
$("fieldset[id='click_info']").hide();
$("fieldset[class^='multi_omics_details']").show();
$("p[id^='gene_id']").html(`Multi-omics data mapped to ${gene_id}`);

}

// // Update the compound names and any details we want on the side panel
function updateOmicsData(returned_data){
//
  console.log("Updating omics data");

  let columns = returned_data.columns;
  let omics_data = returned_data.omics_data;

  let sideDiv =  document.getElementById("dataDiv");
  sideDiv.innerHTML = "";

  for (const [group_name, attribute_list] of Object.entries(omics_data)) {

    let groupDiv = document.createElement('div');
    groupDiv.setAttribute('class', 'p-1');

    let group_header = `<p class= "sidebar">${capital_letter(group_name)}</p>`;

    let group_table = get_omics_gp_table(columns, attribute_list, group_name);

    let group = group_header+group_table;
    groupDiv.innerHTML =  group;
    sideDiv.appendChild(groupDiv);
}

//
//       //Add the tooltips after all divs created.
//       add_side_tooltips()
//     }
}
//
// Returns a single HTML table for a single peak group
function get_omics_gp_table(columns, attribute_list, group_name){
//
//

console.log("getting omics table")

let group_table = `<div class="pl-2 pb-0 table-responsive">
       <table class="table table-sm table-bordered side_table">
     <thead>
            <tr>`
      // Add Table headers from column names
      for (var i = 0; i < columns.length; i++) {
        let head = `<th class=${columns[i]}>${columns[i]}</th>`
        group_table = group_table+head
      };
      //Start the table body
      let data_segment
      group_table = group_table+`<tbody>`
        for (var i = 0; i < attribute_list.length; i++) {
          let current_attributes = attribute_list[i];
          //Add the data for a row
          group_table = group_table+`<tr>`;
          for (var d = 0; d < current_attributes.length; d++) {
          if (group_name=='compounds' && columns[d]=='ID' && current_attributes[d]!==null){
            data_segment =`<td><a href="met_ex_all/${current_attributes[d]}" data-toggle="tooltip"
            title="Compound ${current_attributes[d]}}" target="_blank">${current_attributes[d]}</a></td>`
          }
          else if (group_name=='pathways' && columns[d]=='ID') {
            data_segment=`<td><a href="pathway_search?pathway_search=${current_attributes[d+1]}" data-toggle="tooltip"
            title="${current_attributes[d+1]}} changes in FlyMet tissues" target="_blank">${current_attributes[d]}</a></td>`
          }
          else  {
              data_segment = `<td>${current_attributes[d]}</td>`
            };
            group_table = group_table+data_segment
          }
          //
          group_table = group_table+`</tr>`
          };
 console.log("returning omics table for a group")
 return group_table
//
};
// // Add table header tooltips --these are temporary.
// //KMCL: These tool tips have to be replaced with something responsive - i.e. where the buttons change depending on the data.
// function add_side_tooltips(){
//
//   $('.I').tooltip({title: `This peak has been Identified using a library standard`, placement: "top"});
//   $('.F').tooltip({title: `MS/MS Fragmentation data has been used to identify this peak`, placement: "top"});
//   $('.A').tooltip({title: `This peak also annotates X other compounds`, placement: "top"});
//   $('.Conf').tooltip({title: `The confidence level given to this annotation (see Key)`, placement: "top"});
//   $('.Ion').tooltip({title: `The ion species`, placement: "top"});
//   $('.Mass').tooltip({title: `The neutral mass of the compound associated with this annotation`, placement: "top"});
//   $('.RT').tooltip({title: `The retention time of the compound`, placement: "top"});
//
// };
//
// // Given an array return a simple array index that corresponds to the data in the table
// // Basically this is just columns in Table-1 for the Tissue or Age column
//  function get_data_index(data_table){
//    let data_index = []
//    for (var i = 1; i < data_table[0].length; i++) {
//      data_index.push(i);
//   }
//   return data_index
// };

function capital_letter(str)
{
    str = str.split(" ");
    for (var i = 0, x = str.length; i < x; i++) {
        str[i] = str[i][0].toUpperCase() + str[i].substr(1);
    }
    return str.join(" ");
};

export {
    initialise_gene_table,
    updateGeneSidePanel,
  }
