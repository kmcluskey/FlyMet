import traceback

from django.core.management.base import BaseCommand, CommandError
from loguru import logger

from met_explore.compound_selection import CompoundSelector
from met_explore.helpers import set_log_level_info
from met_explore.peak_selection import PeakSelector
from met_explore.population_scripts import populate_samples, populate_peaks_cmpds_annots, add_related_chebis, \
    populate_peaksamples, populate_analysis_comparisions


# Run from the command line using:
# python manage.py initialisedb 'tissues_life_stages_v2.csv' '67_peak_cmpd_export_1.json' '67_peak_int_export.json' 'flymet_analysis_config.json'
# This should be done after deleting DB and removing all migrations.


class Command(BaseCommand):
    args = 'Takes in the FlyMet tissue/sample csv file [0] along with Peak [1] and Intensity [2] json files ' \
           'exported from PiMP'
    help = 'Takes in the above files assigns peaks to compounds and initialises the FlyMet DB ' \
           'FlyMet DB'

    def add_arguments(self, parser):
        parser.add_argument('sample_csv', type=str)
        parser.add_argument('peak_json', type=str)
        parser.add_argument('int_json', type=str)
        parser.add_argument('analysis_json', type=str)

    def handle(self, *args, **options):

        sample_csv = options['sample_csv']
        peak_json = options['peak_json']
        int_json = options['int_json']
        analysis_json= options['analysis_json']

        try:
            set_log_level_info()
            logger.info("the files we are using are: %s %s %s %s" % (sample_csv, peak_json, int_json, analysis_json))

            # Populate sample information to database
            populate_samples(sample_csv)

            # Populate the information relating to the different Analyses and their comparisons.
            populate_analysis_comparisions(analysis_json)

            # Add Chebi IDs and other identifiers. Additionally ensure Chebi IDs represent unique cmpds.
            peak_select = PeakSelector(peak_json, int_json)
            pre_peak_df = peak_select.pre_process_compounds()

            # Construct peak dataframe, removing duplicates
            construct_peak_df = peak_select.construct_all_peak_df(pre_peak_df)
            peak_df = peak_select.remove_duplicates(construct_peak_df)

            # Populate peak compound annotations to database
            populate_peaks_cmpds_annots(peak_df)
            add_related_chebis()

            # Construct intensity dataframe
            int_df, ids_dict = peak_select.construct_int_df(peak_df)

            # Populate peak intensity information to database for each sample. SLOW.
            populate_peaksamples(int_df, ids_dict)

            # Get peak df selected according to certain criteria
            selected_df, unique_sec_ids = peak_select.get_selected_df(peak_df)

            # Add preferred compounds to peaks
            high_conf_peak_df = peak_select.construct_high_confidence_peak_df(selected_df, unique_sec_ids)

            # Select high confidence compounds and their intensities
            compound_select = CompoundSelector()
            hc_int_df = compound_select.construct_hc_int_df(high_conf_peak_df)
            single_cmpds_df = compound_select.get_single_cmpd_df(hc_int_df)
            compound_select.add_preferred_annotations(single_cmpds_df)
            compound_select.update_std_cmpds()

            logger.info('DB initialisation complete')

        except Exception as e:
            traceback.print_exc()
            raise CommandError(e, "Something went horribly wrong")
