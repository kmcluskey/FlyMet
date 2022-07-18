require('bootstrap/js/dist/tooltip');


// Enable tooltips as a reusable function as most are made dynamically.
function enableTooltips(){
  $('[data-bs-toggle="tooltip"]').tooltip({
      container: 'body'
  });
}

function updateReactomePathway(pathway_id, pathway_name, reactome_token){

  console.log("reactome_token ", reactome_token)
      let dTitleDiv = document.getElementById("diagramTitle"); //diagram_title_div
      dTitleDiv.innerHTML = "";
      //
      let pwyDiv = document.createElement(`p`);
      let pwy_tooltip =  `data-bs-toggle="tooltip" title="${pathway_name} in Reactome"`

      let pwy_info =  `<a href="https://reactome.org/content/detail/${pathway_id}" ${pwy_tooltip} target="_blank">${pathway_name}: Reactome</a>`;
      pwyDiv.innerHTML = pwy_info
      dTitleDiv.appendChild(pwyDiv);

      let diagram = Reactome.Diagram.create({
          "placeHolder": "diagramHolder",
          // "width": 1000,
          // "height": 500
      });

      diagram.loadDiagram(pathway_id);
      // diagram.highlightItem('')
      diagram.onDiagramLoaded(function (loaded) {
            console.info("Loaded ", loaded);

        });

        diagram.setAnalysisToken(reactome_token,'TOTAL')

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
function updatePathwayInfo(returned_data, pathway_name, met_ex_url){
  let cmpd_details = returned_data.cmpd_details
  let cmpds = Object.keys(cmpd_details)
  let no_cmpds = cmpds.length;
  let sideDiv =  document.getElementById("dataDiv");
  sideDiv.innerHTML = "";

  let headerDiv = document.createElement('div');
  headerDiv.setAttribute('class', 'sidebar p-2');
  let cmpd_list = cmpds.toString()

  //Set the header with a link to all metabolites in the cmpd_list
  let url_pwm = `${met_ex_url}/${cmpd_list}`; //pathway metabolites

  let met_tooltip =  `data-bs-toggle="tooltip" title="${pathway_name} metabolites found in Flymet"`

  let metabolite_header = `<a href="${url_pwm}"${met_tooltip} target=_"blank">Metabolites in FlyMet`;
  headerDiv.innerHTML =  metabolite_header;
  sideDiv.appendChild(headerDiv);

  enableTooltips()

  //List all the metabolites in the pathway individually.
  for (var i = 0; i < no_cmpds; i++) {

      let cmpdDiv = document.createElement('div');
      cmpdDiv.setAttribute('class', 'p-2 small');

      let url_cmpd = `${met_ex_url}/${cmpds[i]}`;
      let name = cmpd_details[cmpds[i]].name
      let formula = cmpd_details[cmpds[i]].formula
      let chebi_id = cmpd_details[cmpds[i]].chebi_id
      let related_chebi = cmpd_details[cmpds[i]].related_chebi

      if (related_chebi != null) {
        related_chebi = `or ${related_chebi}`
      }
      else {
        related_chebi = ''
      }

       let cmpd_info = `<div><span><a href="${url_cmpd}" target = _"blank">${name} (ChEBI: ${chebi_id} ${related_chebi}; formula: ${formula})</a></span></div>`
            cmpdDiv.innerHTML =  cmpd_info;
            sideDiv.appendChild(cmpdDiv);
}
}



export {
    updatePathwayInfo,
    updateReactomePathway,
    enableTooltips
  }
