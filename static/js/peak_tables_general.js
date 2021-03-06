require('./init_datatables.js');
const d3 = require('d3');
require('bootstrap/js/dist/tooltip');

const MIN_VAL = 3000;


function initialise_pcompare_table(tableName, lowpoint, midpoint, highpoint, nd_title, ajax_url, headerTips){
    let t0 = performance.now();
    const tName = '#'+tableName;
    console.log("tablename", tName)
    console.log (lowpoint, midpoint, highpoint)

    const dashType = $.fn.dataTable.absoluteOrderNumber({
                value: '-', position: 'bottom'
            });

    // const peak_data = document.getElementById('peak_list').getAttribute('url');

    let table = $(tName).DataTable({

      drawCallback: function(settings){
          /* Add some tooltips for demonstration purposes */
          $('.NotDetected').tooltip({title: nd_title, placement: "top"})
      },

        // responsive: true,
        "scrollY": "100vh",
        "scrollCollapse": true,
        "scrollX": true,
        fixedheader: true,
        colReorder: true,
        ajax: {
          url: `/met_explore/${ajax_url}`,
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
                'type': dashType,
                "createdCell": function (td, cellData, rowData, row, col) {

                    let $td = $(td);
                    let $th = $(".col").eq($td.index());

                      // Different colour scales depending on wether we have log (linearscale) or
                      // exponential (logScale) data
                      let colourLog = d3.scaleLog()
                      .domain([lowpoint, midpoint, highpoint])
                      .range(["#1184fc", "#D6DCE6", "#8e3b3d"]);

                      let colourLinear = d3.scaleLinear()
                      .domain([lowpoint, midpoint, highpoint])
                      .range(["#1184fc", "#D6DCE6", "#8e3b3d"]);

                    //If the column header doesn't include the string Tissue then colour the column.
                    if (!($th.text().includes('Peak ID') || $th.text().includes('m/z') || $th.text().includes('RT'))) {
                        if (!(isNaN(cellData))){ //if the value of the cell is a number then colour it.
                            if (lowpoint > 100){
                              if (cellData==0.00){
                                cellData = MIN_VAL //Can't pass zero to the log so choose minimum value
                              };
                            const colour = colourLog(cellData);
                            $(td).css('background-color', colour)
                          }
                          else {
                            const colour = colourLinear(cellData);
                            $(td).css('background-color', colour)
                          }
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
                        $(td).addClass("NotDetected");
                      }
                      else if (value > 100){ //it is intensity data
                          const num = parseFloat(value).toExponential(2)
                          $td.empty();
                          $td.append(num);
                          $(td).addClass("data");
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
        "initComplete": headerTips

    });

//Return the table so that the it is resuable.

    let t1 = performance.now();
    console.log("Time to initialise the table " + (t1 - t0) + " milliseconds.")
    return table;
};

// This is the fucntion used in the pathway-metabolites pages - for several reasons resuing the
// initialise_pcompare_table (above) didn't work but it could probably be refactored to do so.
function pcompare_pathways_table(tableName, lowpoint, midpoint, highpoint, headerTips){
    let t0 = performance.now();
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
        "initComplete": headerTips
      });

        //Return the table so that the it is resuable.
        let t1 = performance.now();
        console.log("Time to initialise the table " + (t1 - t0) + " milliseconds.")
        return table;
        }

//Update the metabolite side panel depending on which row is selected.
//Let tissue name = the first text sent back from the row (more or less)
function updatePeakSidePanel(obj, pk_side_url, pk_side_text, met_url){
  let peak_id = $(obj).children().first().text();
  console.log("pk_side_text", pk_side_text)
  console.log("peak_side ", pk_side_url)


  const handleUpdate = function(returned_data) {

    let radio_filter = document.getElementById('filtered')
    let radio_all = document.getElementById('all_adducts')
    let radio_all_check = radio_all.checked

    // Update the peak table
    updatePeakData(returned_data, radio_all_check, met_url)

    // Redraw the adduct data if the radio button is clicked.
    $("input[name='radio_adducts']" ).click(function(){
      {updateAdducts(returned_data, met_url)};
    });

};

const url = `/met_explore/peak_explore_annotation_data/${peak_id}`
fetch(url)
.then(res => res.json())//response type
.then(handleUpdate);
//
// find all the paragraphs with id peak in the side panel
let pk_url = `${pk_side_url}${peak_id}`
$("fieldset[id='click_info']").hide();
$("fieldset[class^='peak_details']").show();
$("p[id^='peak_id']").html(`<a href="${pk_url}" target="_blank" >${pk_side_text}${peak_id}</a>`);

}
//
function updateAdducts(returned_data, met_url){

  console.log("Updating adducts with", met_url)
  let radio_all = document.getElementById('all_adducts');
  let radio_all_check = radio_all.checked
  updatePeakData(returned_data, radio_all_check, met_url);
}

// Update the compound names and any details we want on the side panel
function updatePeakData(returned_data, radio_all_check, met_url){

  const cmpd_names = returned_data.cmpd_names;
  const adducts = returned_data.adducts;
  const conf_fact = returned_data.conf_fact;
  const neutral_mass = returned_data.neutral_mass;
  const no_other_cmpds = returned_data.no_other_cmpds;
  const cmpd_ids = returned_data.cmpd_ids;

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

      var nm1 = Number(neutral_mass[i]);
      var nm = nm1.toFixed(4);
      var url_met = `${met_url}${cmpd_id}`

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
        if (radio_all_check || ion=='M+H' || ion=='M-H' || ion=='M'){ //draw if ion = M+H or M-H or if all adducts are chosen

        let peakDiv = document.createElement('div');
        peakDiv.setAttribute('class', 'p-2');

        let peak_info = `<span class="${identified} badge badge-pill badge-${success}">${badge_info}</span>
        <span id="cmpd_name" class="peak_data"><a href="${url_met}" target="_blank">${name}</a></span><div class="row pt-2">
        <div id ="Ion" class="col-sm-5 peak_data"><b>Ion: </b>${ion}</div>
        <div id ="NM" class="col-sm-7 peak_data"><b>Mass: </b>${nm}</div><br></div>`;
        peakDiv.innerHTML =  peak_info;
        sideDiv.appendChild(peakDiv);

      }
      add_side_tooltips(id_name, frag_name, no_other_cmpds); //Add the tooltips after all divs created.
    }
};

function get_lifestage(ls_string){

  let ls = "";
  if (ls_string=="(F)")
    ls ="Females";
  else if (ls_string=="(M)")
      ls ="Males";
  else if (ls_string=="(L)")
        ls ="Larvae";

  return ls
};

//KMCL: These tool tips have to be replaced with something responsive - i.e. where the buttons change depending on the data.
function add_side_tooltips(id_name, frag_name, no_other_cmpds){
  $('.I').tooltip({title: `This MS peak has been Identified as ${id_name} using a library standard`, placement: "top"});
  $('.F').tooltip({title: `MS/MS Fragmentation data suggests that this peak is likely to be ${frag_name}`, placement: "top"});
  $('.A').tooltip({title: `This peak also annotates ${no_other_cmpds} other compounds`, placement: "top"});
}

function pathways_pcompare_table(tableName, lowpoint, midpoint, highpoint){
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
                      let tissue ="";
                      let string ="";
                      let ls="";

                      if (head_split[0]=="m/z"){
                        string = "mass-to-charge ratio";
                      }
                      else if (head_split[0]=="Peak"){
                        string ="";
                      }
                      else if (head_split[0]=="RT"){
                        string ="Retention Time";
                      }
                      else {
                        tissue =`Fold change between ${head_split[0]} tissue from`;
                        const header_words = head_split.length;
                        const ls_check = header_words-1;
                        ls = get_lifestage(head_split[ls_check])
                        string = `${tissue} ${ls} and Whole ${ls} flies`
                      }
                        //Change the title attribute of the column to the string/tooltip info
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

    return table;
}

export {
    initialise_pcompare_table, pcompare_pathways_table,
    updatePeakSidePanel, updateAdducts, get_lifestage
  }
