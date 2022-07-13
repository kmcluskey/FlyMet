require('./init_datatables.js');
const d3 = require('d3');
require('bootstrap/js/dist/tooltip');

function initialise_compare_list_table(tableName, lowpoint, midpoint, highpoint, headerTips){
    const tName = '#'+tableName;

    const dashType = $.fn.dataTable.absoluteOrderNumber({
                value: '-', position: 'bottom'
            });


    let table = $(tName).DataTable({

      drawCallback: function(settings){
            /* Add some tooltips for demonstration purposes */
            $('.NotDetected').tooltip({title: "Intensity data was not detected for this tissue/lifestage combinaton.", placement: "top"})
        },
        // responsive: true,
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
            // {className: "maxpx300", "targets":0 }, //First column minumum size of 300px
            {sType: "num-html", "targets":0 },
            {
                "targets": '_all',
                'type': dashType,
                "createdCell": function (td, cellData, rowData, row, col) {

                    let $td = $(td);

                    let $th = $td.closest('table').find('th').eq($td.index());

                        let colourLinear = d3.scaleLinear()
                        .domain([lowpoint, midpoint, highpoint])
                        .range(["#1184fc", "#D6DCE6", "#8e3b3d"]);

                      //If the column header doesn't include the string Tissue then colour the column.

                      if (!($th.text().includes('Metabolite'))) {
                          if (cellData !=='-') {
                            const colour = colourLinear(cellData);
                            $(td).css('background-color', colour)
                          }
                        };

                    if ($th.text().includes('Metabolite')){
                      $(td).addClass("maxpx300")
                    };
                }
            }
        ],
        // Add the tooltips to the dataTable header
        "initComplete": headerTips
    })
//Return the table so that the it is resuable.
    return table;
}

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
                        link = link+'<a href=https://www.ebi.ac.uk/chebi/searchId.do?chebiId='+cell_data+' target=_blank>'+cell_data+'</a>'+linker
                      }
                      else if (cell_data.startsWith('HMDB')){
                        link = link+'<a href=http://www.hmdb.ca/metabolites/'+cell_data+' target=_blank>'+cell_data+'</a>'+linker
                      }
                      else if (cell_data.startsWith('C')){
                        link = link+'<a href=https://www.genome.jp/dbget-bin/www_bget?cpd:'+cell_data+' target=_blank>'+cell_data+'</a>'+linker
                      }
                      else if (cell_data.startsWith('LM')){
                        link = link+'<a href=http://www.lipidmaps.org/data/LMSDRecord.php?LMID='+cell_data+' target=_blank>'+cell_data+'</a>'+linker
                      }
                      }
                      return link;
                      }
                    }
        ],
})
    return table;
}

function updatePathwayPanel(obj, pathway_url){
  let currentRow = $(obj).closest("tr");
  let cmpd_id = $('#metabolite_list').DataTable().row(currentRow).data()[0];
  let cmpd_name = $(obj).children().first().text();

  console.log("PWY_URL1", pathway_url)

  // Returned data is the data returned from the url below.
  const handleUpdate = function(returned_data) {

    console.log("PWY_URL", pathway_url)

    // updatePathways(returned_data, pathways_url)

    let pwyDiv =  document.getElementById("pathwayDetails");
    pwyDiv.innerHTML = "";

    let pwy_dict = returned_data.pwy_data;
    let no_pwys = Object.keys(pwy_dict).length

    if (no_pwys === 0){
      let pwy_text = `<p> There are currently no Pathways mapped to ${cmpd_name}</p>`
      let groupDiv = document.createElement('div');
      groupDiv.setAttribute('class', 'p-1');
      groupDiv.innerHTML =  pwy_text;
      pwyDiv.appendChild(groupDiv)
    }
    else {
        for (var pwy_id in pwy_dict) {
            console.log("adding pwy_id")
            let groupDiv = document.createElement('div');
            groupDiv.setAttribute('class', 'p-1');
            let pwy_name = pwy_dict[pwy_id]['display_name'];
            // let pwy_name = details['display_name']
            // let pathway_name = escape(pwy_name)

            let pwy_url =`<a href="${pathway_url}?${pathway_url}=${pwy_id}" data-toggle="tooltip"
            title="${pwy_name} changes in FlyMet tissues" target="_blank">${pwy_name}</a>`
            groupDiv.innerHTML =  pwy_url;
            pwyDiv.appendChild(groupDiv)
      }
    } }
  const pwy_url = `/met_explore/met_ex_pathway_data/${cmpd_id}`
  fetch(pwy_url)
  .then(res => res.json())//response type
  .then(handleUpdate);

  // find all the paragraphs with id peak in the side panel
  $("#pathwaysDiv").show();
  $("legend[id^='pwy_name']").text(`Pathways associated with ${cmpd_name}`);

};

function updateGenePanel(obj, gene_url){
  const num_cols = 6;
  let currentRow = $(obj).closest("tr");
  let cmpd_id = $('#metabolite_list').DataTable().row(currentRow).data()[0];
  let cmpd_name = $(obj).children().first().text();

  // Returned data is the data returned from the url below.
  const handleUpdate = function(returned_data) {
    // updatePathways(returned_data, pathways_url)

    let geneDiv =  document.getElementById("geneDetails");
    geneDiv.innerHTML = "";

    let gene_dict = returned_data.gene_data;
    let no_genes = Object.keys(gene_dict).length
    console.log("The number of genes are ", no_genes)

    let gene_list = Object.keys(gene_dict)
    let gene_list_url = `<a href="${gene_url}/${gene_list}" data-toggle="tooltip"
    title="All ${cmpd_name} associated genes" target="_blank">All genes associated with ${cmpd_name}</a>`


    if (no_genes === 0){
      let gene_text = `<p> There are currently no Genes mapped to ${cmpd_name}</p>`
      let groupDiv = document.createElement('div');
      groupDiv.setAttribute('class', 'p-1');
      groupDiv.innerHTML =  gene_text;
      geneDiv.appendChild(groupDiv)
    }
    else {

        //Make a div to hold the gene group
        let groupDiv = document.createElement('div');
        groupDiv.setAttribute('class', 'p-1');
        // Make a new row
        let rowDiv = document.createElement('div');
        rowDiv.setAttribute('class', 'row');
        // for each row
        let i=0
        for (var gene_id in gene_dict) {

        if (i<num_cols) {
          i++;
              let gene_name = gene_dict[gene_id]['display_name'];
              let dy_gene_url =`<a href="${gene_url}/${gene_id}" data-toggle="tooltip"
              title="${gene_name} gene" target="_blank">${gene_name}</a>`
              //Make and populate a column
              let colDiv = document.createElement('div');
              colDiv.setAttribute('class', 'col-sm')
              colDiv.innerHTML =  dy_gene_url;
              rowDiv.appendChild(colDiv)
            }
            else { //we are out of columns so make a new row with i=1 as we add a gene to the row
              i=1
              // Append row onto group and make a new row
              geneDiv.appendChild(rowDiv);
              rowDiv = getRowDiv();

              let gene_name = gene_dict[gene_id]['display_name'];
              let dy_gene_url =`<a href="${gene_url}/${gene_id}" data-toggle="tooltip"
              title="${gene_name} gene" target="_blank">${gene_name}</a>`

              let colDiv = document.createElement('div');
              colDiv.setAttribute('class', 'col-sm')
              colDiv.innerHTML =  dy_gene_url;
              rowDiv.appendChild(colDiv)
      }
    }
    geneDiv.appendChild(rowDiv);
    // Add final list
    let colDiv = document.createElement('div');
    colDiv.setAttribute('class', 'col-sm');
    colDiv.innerHTML =  `<br>${gene_list_url}`;
    rowDiv = getRowDiv();
    rowDiv.appendChild(colDiv);
    geneDiv.appendChild(rowDiv);

  }}
  const url = `/met_explore/met_ex_pathway_data/${cmpd_id}`
  fetch(url)
  .then(res => res.json())//response type
  .then(handleUpdate);

  // find all the paragraphs with id peak in the side panel
  $("#geneDiv").show();
  $("legend[id^='gene_name']").text(`Genes associated with ${cmpd_name}`);

};

function getRowDiv(obj){
  let rowDiv = document.createElement('div');
  rowDiv.setAttribute('class', 'row');
  return rowDiv
}

//Update the metabolite side panel depending on which row is selected.
//Let tissue name = the first text sent back from the row (more or less)
function updateMetboliteSidePanel(obj, peak_url){

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
  updatePeakData(returned_data, radio_all_check, cmpd_name, peak_url)
  //
    // Redraw the adduct data is the radio button is clicked.
    $("input[name='radio_adducts']" ).click(function(){
      {updateAdducts(returned_data, cmpd_name, peak_url)};
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


function updateAdducts(returned_data, cmpd_name, pk_url){
//
  console.log("Updating adducts")
  let radio_all = document.getElementById('all_adducts');
  let radio_all_check = radio_all.checked
  updatePeakData(returned_data, radio_all_check, cmpd_name, pk_url);
 }

// Update the compound names and any details we want on the side panel
function updatePeakData(returned_data, radio_all_check, cmpd_name, pk_url){

  console.log("Updating peak data")

  const peak_groups = returned_data.peak_groups;
  const columns = returned_data.columns;
  const total_peak_list = returned_data.peak_list;

  console.log("peak_groups", peak_groups)
  console.log ("peak_list", total_peak_list)

  // make a div so that we can click through to all peaks for a metabolite
  let allPeakDiv = document.getElementById("allPeaks")
  allPeakDiv.innerHTML = "";
  let peakDiv = document.createElement('div');
  peakDiv.setAttribute('class', 'p-1');
  let all_peaks_url = `${pk_url}${total_peak_list}`
  let all_peaks_header = `<hr class="my-2"><a class="highlight" href="${all_peaks_url}" target="_blank">All Peaks annotated for ${cmpd_name}</a>`

  peakDiv.innerHTML = all_peaks_header
  allPeakDiv.appendChild(peakDiv);


  let sideDiv =  document.getElementById("dataDiv");
  sideDiv.innerHTML = "";

  let no_groups = peak_groups.length
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
        let this_peak = peak_group[j]
        if (this_peak['adduct']=='M+H' || this_peak['adduct']=='M-H' || this_peak['adduct']=='M'){
          m_adduct =true;
        }
      }
    // If the radio check is all or the group contains an M+H or M-H adduct add the peak group table
      if (radio_all_check || m_adduct){

        console.log("peak_gp", peak_group)

        let peak_ids =""
        for (var p = 0; p < items_in_gp; p++){
          let this_peak = peak_group[p];
          peak_ids = peak_ids+this_peak['peak_id']+",";
        }

        let peak_list = peak_ids.substring(0,peak_ids.length-1) //remove last "," from string the lazy way
        console.log("peak_ids are now", peak_ids)
        peak_group_no = peak_group_no+1;
        let url_pg = `${pk_url}${peak_list}`
        console.log("url_pg", url_pg)
        let group_header = `<hr class="my-2"><p class= "sidebar"><a class="highlight" href="${url_pg}" target="_blank">Peak Group: ${peak_group_no}</a></p>`
        let group_table = get_peak_gp_table(columns, peak_group, cmpd_name, pk_url);
        let group = group_header+group_table;
        groupDiv.innerHTML =  group;
        sideDiv.appendChild(groupDiv);
      }

      //Add the tooltips after all divs created.
      add_side_tooltips()
    }
}

// Returns a single HTML table for a single peak group
function get_peak_gp_table(columns, peak_group, cmpd_name, pk_url){


  let group_table = `<div class="pl-2 pb-0 table-responsive">
      <table class="table table-sm table-bordered side_table">
      <thead>
        <tr>`

      // Add Table headers from column names
      for (var i = 0; i < columns.length; i++) {
        let head = `<th class=${columns[i]}>${columns[i]}</th>`
        group_table = group_table+head
      }

        group_table = group_table+`<thead>
        <tr> <tbody>`

        let peaks_in_gp = peak_group.length;
        for (var i = 0; i < peaks_in_gp; i++) {
          let this_group=peak_group[i];
          let peak_id = this_group['peak_id'];
          let peak_url = `${pk_url}${peak_id}`

          let ion = this_group['adduct'];
          let nm1 = Number(this_group['nm']);
          let nm = nm1.toFixed(4);
          let rt1 = Number(this_group['rt']);
          let rt =  rt1.toFixed(2);

          let no_other_cmpds = this_group['no_adducts']-1 //Remove one for this compound.
          let conf =  this_group['conf']

          let identified, badge_info, success, id_name, frag_name, data_list

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


          group_table = group_table +`<tr><td class="badge badge-pill badge-${success}">${badge_info}</td><td><a href="${peak_url} "target="_blank">${peak_id}<a></td>`
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

// Given an array return a simple array index that corresponds to the data in the table
// Basically this is just columns in Table-1 for the Tissue or Age column
 function get_data_index(data_table){
   let data_index = []
   for (var i = 1; i < data_table[0].length; i++) {
     data_index.push(i);
  }
  return data_index
};

export {
    initialise_compare_list_table,
    initialise_met_table,
    updateMetboliteSidePanel,
    updatePathwayPanel,
    updateGenePanel,
    get_data_index
  }
