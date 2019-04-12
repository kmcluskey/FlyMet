from django.core.management.base import BaseCommand, CommandError
from met_explore.population_scripts import *
from met_explore.peak_selection import PeakSelector
from met_explore.compound_selection import CompoundSelector

import argparse
from sys import stdin

# Run from the command line using:
# python manage.py initialisedb 'tissues_life_stages_v2.csv' '67_peak_cmpd_export_1.json' '67_peak_int_export.json'
# This should be done after deleting DB and removing all migrations.


class Command(BaseCommand):
    args ='Takes in the FlyMet tissue/sample csv file [0] along with Peak [1] and Intensity [2] json files ' \
          'exported from PiMP'
    help='Takes in the above files assigns peaks to compounds and inialises the FlyMet DB ' \
         'FlyMet DB'

    def add_arguments(self, parser):
        parser.add_argument('sample_csv', type=str)
        parser.add_argument('peak_json', type=str)
        parser.add_argument('int_json', type=str)


    def handle(self, *args, **options):

        sample_csv = options['sample_csv']
        peak_json = options['peak_json']
        int_json = options['int_json']

        try:
            print("the files we are using are:", sample_csv, peak_json, int_json)

            populate_samples(sample_csv)
            peak_select = PeakSelector(peak_json, int_json)
            peak_df = peak_select.construct_high_confidence_peak_df()
            populate_filtered_peaks_cmpds(peak_df)
            int_df, ids_dict = peak_select.construct_int_df(peak_df)
            populate_peaksamples(int_df, ids_dict)

            # Add preferred compounds to peaks
            compound_select = CompoundSelector()
            compound_select.add_preferred_annotations()


        except Exception as e:
            print (e)
            raise CommandError(e, "Something went horribly wrong")
