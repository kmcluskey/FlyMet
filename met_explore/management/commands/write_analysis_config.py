import json
import pandas as pd

from django.core.management.base import BaseCommand, CommandError
from loguru import logger


# Run from the command line using:
# python manage.py write_analysis_config 'tissues_life_stages_v2.csv' 'cat_groups'

# This should be done after deleting DB and removing all migrations.

# If the correct sample csv is read in and caterory groups the config file will be produced by this script for use in the
# initialisation script - This is FlyMet specific.

"""The cat_groups is the category_name, description, and the analysis_sets
            For FlyMet the following is read in:
[{
  "category_name": "Tissues",
  "description": "FlyMet Tissue Analysis",
  "analysis_sets": { "Tissue Comparisons": ["case_control", "tissue", "whole_tissue"],
                    "M/F Comparisons": [ "case_control", "tissue", "m_f"]}
},
{
  "category_name": "Age",
  "description": "FlyMet Aged Flies Analysis",
  "analysis_sets": { "Age Comparisons": ["case_control", "age", "whole_tissue"],
  "Age M/F Comparisons": ["case_control", "age", "m_f"]}
  }]"""

class Command(BaseCommand):
    args = 'Takes in the FlyMet tissue/sample csv file'
    help = 'Takes in the sample csv file and a comparisons_groups dict from FlyMet and generates the analysis_config file'

    def add_arguments(self, parser):
        parser.add_argument('sample_csv', type=str)
        parser.add_argument('comparisons_groups', type=str)

    def handle(self, *args, **options):

        sample_csv = options['sample_csv']
        comparisons_groups = options['comparisons_groups']

        skeleton_config = {
            "projects": [
                {
                    "project_name": "FlyMet",
                    "project_description": "Tissue Atlas plus Aged flies for Drosophila",
                    "metabolomics": {
                        "sample_csv": "data/peak_data/tissues_life_stages_combine_whole_flymet4.csv",
                        "peak_json": "data/peak_data/1724_peak_cmpd_export.json",
                        "int_json": "data/peak_data/1724_peak_int_export.json"
                    }
                }
            ]
        }
        
        try:

            logger.info("The files for writing the analysis_config are using are: %s %s" % (sample_csv, comparisons_groups))

            sample_details = pd.read_csv(sample_csv, index_col=0).dropna(how='all')

            f = open(comparisons_groups)
            x = f.read()
            cat_groups = json.loads(x)

            logger.info("Constructing the analysis config file")

            unique_groups = set(sample_details.group.values)
            cat_list = []  # List of dictionaries
            for c in cat_groups:
                cat_dict = {
                    "category_name": c["category_name"],
                    "description": c["description"]
                }
                analysis_list = []

                for gc, analysis_details in c['analysis_sets'].items():

                    # For flymet these are the different case and control groups -
                    # they are filtered later depending on the analysis group.

                    m_f_controls = [x for x in unique_groups if x.endswith('_f')]
                    m_f_cases = [x for x in unique_groups if x.endswith('_m')]
                    print(m_f_cases)
                    whole_factor_controls = ["Whole_f", "Whole_m", "Whole_l"]
                    whole_factor_cases = [x for x in unique_groups if x not in whole_factor_controls]

                    case_control_dict = {'whole_tissue': [whole_factor_cases, whole_factor_controls],
                                         'm_f': [m_f_cases, m_f_controls]}

                    comparisons_list = []
                    analysis_group = analysis_details[1]
                    control_case_group = analysis_details[2]
                    case_controls = case_control_dict[control_case_group]
                    all_cases = case_controls[0]

                    # Get cases for specific analysis group (tissue or age)

                    """
                    Given the analysis group (tissue or age) and all the potential cases, return the cases 
                    just for this analysis group for FlyMet the analysis groups are determined by which 
                    factors the samples are for.
                    """
                    cases = []

                    for case in all_cases:
                        group_value = sample_details[sample_details.group == case][analysis_group].values[0]
                        in_group = pd.notnull(group_value)
                        if in_group:  # if the sample is in this group
                            cases.append(case)

                    controls = case_control_dict[control_case_group][1]
                    control, c_name = None, None

                    for case in cases:
                        if control_case_group.startswith('whole'):
                            ls = case[-1]  # last letter of the string
                            control = [x for x in controls if x.endswith(ls)][0]
                            c_name = case + "/" + control
                        elif control_case_group.startswith('m_f'):
                            try:
                                tissue = case.split("_")[0]
                                control = [x for x in controls if x.startswith(tissue)][0]
                                c_name = case + "/" + control
                            except IndexError:
                                logger.warning(
                                    "There is no control for this case eg Testes (no female) %s so skipping" % case)
                                continue

                        comparison_dict = {
                            "comparison_name": c_name,
                            "case": case,
                            "control": control
                        }
                        comparisons_list.append(comparison_dict)

                    a_dict = {
                        "analysis_name": gc,
                        "analysis_type": analysis_details[0],
                        "comparisons": comparisons_list
                    }
                    analysis_list.append(a_dict)
                    cat_dict["analysis_sets"] = analysis_list
                cat_list.append(cat_dict)
            # This only works if there is a single project  skeleton_config["projects"][0]
            skeleton_config["projects"][0]['metabolomics']["categories"] = cat_list

            try:
                with open("data/flymet_analysis_config_new.json", 'w') as file:
                    json.dump(skeleton_config, file)
                logger.info("The flymet configuration file has been written")

            except TypeError as e:
                logger.error("Unable to dump the analysis config dict with error %s " % e)

        except Exception as e:

            logger.error("Failed with %s" % e)
