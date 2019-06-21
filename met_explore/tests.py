from django.test import TestCase

# Create your tests here.

from met_explore.peak_selection import PeakSelector
from met_explore.preprocessing import PreprocessCompounds
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# model = cobra.io.read_sbml_model('/Users/Karen/flymet_webstuff/notebooks/fly_pwt.xml')



def test_email():
    # using SendGrid's Python Library
    # https://github.com/sendgrid/sendgrid-python

    message = Mail(
        from_email='webmaster@flymet.org',
        to_emails='webmaster@flymet.org',
        subject='Sending with Twilio SendGrid is Fun',
        html_content='<strong>and easy to do anywhere, even with Python</strong>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

def run_preprocessing_script():

    """
    Method to run the population script
    """
    peak_select = PeakSelector('/Users/Karen/FlyOmics/data/1160_peak_cmpd_export.json',
                               '/Users/Karen/FlyOmics/data/1160_peak_int_export.json')

    peak_df = peak_select.pre_process_compounds()

    return peak_df

def test_processing_cmpds(peak_df):

    process_cmpds = PreprocessCompounds(peak_df)

    peak_df = process_cmpds.get_preprocessed_cmpds()


def cmpd_param_check(param, peak_chebi_df):
    """

    :param param: The dataframe parameter that you are interested in
    :param peak_chebi_df: the DF with all the parameters

    :return:
    """
    cmpd_param = peak_chebi_df[param].unique()
    for cmpd in cmpd_param:
        single_cmpd_df = peak_chebi_df[peak_chebi_df[param] == cmpd]

        cmpd_ids = single_cmpd_df.cmpd_id.unique()
        no_cmpd_ids = len(cmpd_ids)

        if no_cmpd_ids > 1:
            print("More than one cmpd_id with this", param)
            print(single_cmpd_df)