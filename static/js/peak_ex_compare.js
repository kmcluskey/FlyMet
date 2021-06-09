import {get_lifestage, initialise_pcompare_table, updatePeakSidePanel} from './peak_tables_general.js';

function headerTips(settings) {

    $(".col").each(function () {

        let $td = $(this);
        let header = $td.text();
        let head_split = header.split(" ");
        let tissue = "";
        let string = "";
        let ls = "";

        if (head_split[0] == "m/z") {
            string = "mass-to-charge ratio";
        } else if (head_split[0] == "Peak") {
            string = "";
        } else if (head_split[0] == "RT") {
            string = "Retention Time";
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
                string = `${head_split[0]} and ${control_label}`
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

//
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
// };

$(document).ready(function () {
    $("fieldset[class^='peak_details']").hide();
    console.log("peak compare list", peak_compare_list)

    let nd_title = "This MS peak was not detected for this tissue/life stage combination";
    let ajax_url = `peak_compare_data/${analysis_id}/${peak_compare_list}`;
    let peak_side_url = `peak_explorer/${analysis_id}/`;
    let peak_side_text = `Intensities for peak `;
    let met_url = `met_ex_all/${analysis_id}/`;

    let peak_table = initialise_pcompare_table("peak_list", min_value, mean_value, max_value,
        nd_title, ajax_url, headerTips);

    peak_table.on('click', 'tr', function () {
        updatePeakSidePanel(this, peak_side_url, peak_side_text, met_url);
    });

});
