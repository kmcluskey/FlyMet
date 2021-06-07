Awesomplete = require('awesomplete');
require('awesomplete/awesomplete.css');
require('../css/awesomechanges.css')



async function loadData(viewUrl) {
  try {
    const result = await $.getJSON(viewUrl);
    return result;
  } catch (e) {
    console.log(e);
  }
}


$(document).ready(function() {

  //Method to add an autocomplete search function to the DB
  loadData((url)).then(function(data) {
    new Awesomplete(metabolite_search_age, {list: data.metaboliteNames});
  });
  loadData((pwy_url)).then(function(data) {
  new Awesomplete(pathway_age_search, {list: data.pathwayNames});
  new Awesomplete(pathway_age_metabolites, {list: data.pathwayNames});
  });
});
