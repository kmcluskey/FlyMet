import traceback
import json

from django.core.management.base import BaseCommand, CommandError
from loguru import logger

from django.contrib.auth import get_user_model
from met_explore.compound_selection import CompoundSelector
from met_explore.constants import CONFIG_METABOLOMICS, SAMPLE_CSV, PEAK_JSON, INT_JSON, CONFIG_PROJECT, PROJECT_NAME, \
    PROJECT_DESC
from met_explore.helpers import set_log_level_info
from met_explore.models import Project, Share
from met_explore.peak_selection import PeakSelector
from met_explore.population_scripts import populate_samples, populate_peaks_cmpds_annots, add_related_chebis, \
    populate_peaksamples


# Run from the command line using:
# python manage.py initialisedb 'tissues_life_stages_v2.csv' '67_peak_cmpd_export_1.json' '67_peak_int_export.json'
# This should be done after deleting DB and removing all migrations.

User = get_user_model()


class Command(BaseCommand):
    args = 'Takes in the FlyMet tissue/sample csv file [0] along with Peak [1] and Intensity [2] json files ' \
           'exported from PiMP'
    help = 'Takes in the above files assigns peaks to compounds and inialises the FlyMet DB ' \
           'FlyMet DB'

    def add_arguments(self, parser):
        parser.add_argument('config_json', type=str) # optional

    def handle(self, *args, **options):

        config_path = options['config_json']
        with open(config_path) as json_file:
            configs = json.load(json_file)

        # create user and project
        project_options = configs[CONFIG_PROJECT]
        project_name = project_options[PROJECT_NAME]
        project_desc = project_options[PROJECT_DESC]
        metadata = {}
        project = Project.objects.create(name=project_name,
                                          description=project_desc,
                                          metadata=metadata)

        user_name = project_options['user_name']
        current_user = User.objects.create_user(username=user_name, password=user_name)
        share = Share(user=current_user, project=project, read_only=False, owner=True)
        share.save()

        # load metabolomics data
        if CONFIG_METABOLOMICS in configs:
            try:
                set_log_level_info()
                metabo_options = configs[CONFIG_METABOLOMICS]
                sample_csv = metabo_options[SAMPLE_CSV]
                peak_json = metabo_options[PEAK_JSON]
                int_json = metabo_options[INT_JSON]
                logger.info("the files we are using are: %s %s %s" % (sample_csv, peak_json, int_json))

                # Populate sample information to database
                populate_samples(project, sample_csv)

                # Add Chebi IDs and other identifiers. Additionally ensure Chebi IDs represent unique cmpds.
                peak_select = PeakSelector(peak_json, int_json)
                pre_peak_df = peak_select.pre_process_compounds()

                # Construct peak dataframe, removing duplicates
                construct_peak_df = peak_select.construct_all_peak_df(pre_peak_df)
                peak_df = peak_select.remove_duplicates(construct_peak_df)

                # Populate peak compound annotations to database
                populate_peaks_cmpds_annots(project, peak_df)
                add_related_chebis()

                # Construct intensity dataframe
                int_df, ids_dict = peak_select.construct_int_df(peak_df)

                # Populate peak intensity information to database for each sample. SLOW.
                populate_peaksamples(int_df, ids_dict, project)

                # Get peak df selected according to certain criteria
                selected_df, unique_sec_ids = peak_select.get_selected_df(peak_df)

                # Add preferred compounds to peaks
                high_conf_peak_df = peak_select.construct_high_confidence_peak_df(selected_df, unique_sec_ids)

                # Select high confidence compounds and their intensities
                compound_select = CompoundSelector(project)
                hc_int_df = compound_select.construct_hc_int_df(high_conf_peak_df)
                single_cmpds_df = compound_select.get_single_cmpd_df(hc_int_df)
                compound_select.add_preferred_annotations(single_cmpds_df)
                compound_select.update_std_cmpds()

                project.metadata.update({
                    CONFIG_METABOLOMICS: metabo_options
                })
                project.save()
                logger.info('Completed')

            except Exception as e:
                traceback.print_exc()
                raise CommandError(e, "Something went horribly wrong")
