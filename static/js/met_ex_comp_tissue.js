require('./init_datatables.js');
const d3 = require('d3');
require('bootstrap/js/dist/tooltip');
import {initialise_compare_list_table} from './metabolite_tables_general';
import {get_lifestage} from './peak_tables_general';

function headerTips(settings) {

    $(".col").each(function () {

        let $td = $(this);
        let header = $td.text();
        let head_split = header.split(" ");
        let tissue = "";
        let string = "";
        let ls = "";

        if (head_split[0] == "Metabolite") {
            string = "Identified Metabolite";
        } else {
            if (is_fly_tissue_data) {
                tissue = `Fold change between ${head_split[0]} tissue from`;
                const header_words = head_split.length;
                const ls_check = header_words - 1;
                ls = get_lifestage(head_split[ls_check])
                string = `${tissue} ${ls} and Whole ${ls}`
            } else if (is_fly_age_data) {
                tissue = `Fold change between ${head_split[0]} day old`;
                const header_words = head_split.length;
                const ls_check = header_words - 1;
                ls = get_lifestage(head_split[ls_check])
                string = `${tissue} ${ls} and Whole (7 day old) ${ls}`
            } else {
                tissue = `Fold change between ${case_label} from`;
                const header_words = head_split.length;
                const ls_check = header_words - 1;
                ls = get_lifestage(head_split[ls_check])
                string = `${tissue} ${head_split[0]} and ${control_label}`
            }
        }
        //Change the title attribute of the column to the string/tooltip info
        $td.attr({title: `${string}`});
        $td.attr('data-toggle', "tooltip");
        $td.attr('data-placement', "top");
    });
    /* Apply the tooltips */
    $('[data-toggle="tooltip"]').tooltip({
        container: 'body'
    });

};

$(document).ready(function () {
    let met_table = initialise_compare_list_table("compare_list", min_value, mean_value, max_value, headerTips);

});
