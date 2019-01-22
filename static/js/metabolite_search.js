//This is the JavaScript that is required for the metabolite_search page.
import {initialise_table} from './flymet_tables';
import {singleMet_intensity_chart} from './flymet_highcharts.js';
import {test_chart} from './flymet_highcharts.js';

//Update the metabolite side panel depending on which row is selected.
//Let tissue name = the first text sent back from the row (more or less)
function updateMetSidePanel(obj){
    let tissue_name = $(obj).children().first().text();

    // find all the paragraphs with id peak in the side panel

    $("fieldset[id='click_info']").hide();
    $("fieldset[class^='peak_details']").show();
    $("p[id^='tissue_type']").text('Intensities in ' +tissue_name);

    singleMet_intensity_chart('highchart');
    singleMet_intensity_chart('highchart1');
    singleMet_intensity_chart('highchart2');

    // Add table header tooltips --these are temporary.
    //KMCL: These tool tips have to be replaced with something responsive - i.e. where the buttons change depending on the data.

    $('#I').tooltip({title: "MS peak has been Identified as Histidine using a library standard", placement: "top"});
    $('#I2').tooltip({title: "MS peak has been Identified as Histidine using a library standard", placement: "top"});
    $('#F').tooltip({title: "MS/MS Fragmentation data suggests that a peak is 96.2% likely to be Histidine", placement: "top"});
    $('#F1').tooltip({title: "MS/MS Fragmentation data suggests that a peak is 99% likely to be Histidine", placement: "top"});
    $('#A').tooltip({title: "This peak, annotated as Histidine, also annotates 15 other compounds", placement: "top"});
    $('#A1').tooltip({title: "This peak, annotated as Histidine, also annotates 4 other compounds", placement: "top"});
    $('#A2').tooltip({title: "This peak, annotated as Histidine, also annotates 47 other compounds", placement: "top"});
    $('#F0').tooltip({title: "There is no fragmenetation data associated with this peak", placement: "top"});


}

function add_met_tooltips(obj){

    $('.AM_met_WT_ratio').tooltip({title: "Fold Change of metabolite Intensity in Adult Male vs Whole Fly", placement: "top"});
    $('.AF_met_WT_ratio').tooltip({title: "Fold change of metabolite Intensity in Adult Female vs Whole Fly", placement: "top"});
    $('.L_met_WT_ratio').tooltip({title: "Fold change of metabolite Intensity in Larvae vs Whole Fly", placement: "top"});

}

$(document).ready(function() {

    $("fieldset[class^='peak_details']").hide();

    let met_table = initialise_table("example", 0.0, 1.0, 3.0);
    add_met_tooltips(met_table);

    met_table.on( 'click', 'tr', function () {
        updateMetSidePanel(this);
    } )

});
