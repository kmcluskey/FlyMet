from django.test import TestCase

# Create your tests here.

# import cobra
from met_explore.preprocessing import PreprocessCompounds
# model = cobra.io.read_sbml_model('/Users/Karen/flymet_webstuff/notebooks/fly_pwt.xml')

def run_preprocessing_script():

    """
    Method to run the population script
    """

    preprocess = PreprocessCompounds('data/1160_peak_cmpd_export.json')

    preprocess.get_preprocessed_cmpds()



