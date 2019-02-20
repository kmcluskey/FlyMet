from met_explore.models import Peak, SamplePeak, Sample

import collections
import pandas as pd
import numpy as np
import operator

import logging
logger = logging.getLogger(__name__)

## A class that contains various methods for selecting compounds from the peak object

class CompoundSelector(object):

    def __init__(self):

        self.int_df = self.get_cmpd_intensity_df()
        self.single_cmpds_df = self.get_single_cmpd_df()



    def get_cmpd_intensity_df(self):
        """
        :return:  # A df with all of the samples and their intensities for all of the peaks
        # Index is peak sec ids and Metabolite column has the compound name.
        """
        samples = Sample.objects.all()
        peaks = Peak.objects.all()

        df_index = [p.psec_id for p in peaks]
        cmpds = [p.cmpd_name for p in peaks]
        columns = [s.name for s in samples]
        int_df = pd.DataFrame(index=df_index, columns=columns, dtype=float)

        for i in df_index:
            for c in columns:
                sp = SamplePeak.objects.get(peak__psec_id=i, sample__name=c)
                int_df.at[i, c] = sp.intensity

        int_df.insert(0, 'Metabolite', cmpds)

        return int_df


    # This returns a DF with the groups/tissues and their average intensities and a maximum intensity for the row.
    def get_group_df(self, int_df):

        samples = Sample.objects.all()
        sample_groups = set([sp.group for sp in samples])
        df_index = list(int_df.index.values)
        group_df = pd.DataFrame(index=df_index, columns=sample_groups, dtype=float)

        for group in sample_groups:
            gp_samples = Sample.objects.filter(group=group)
            for i in df_index:
                int_list = []
                for g in gp_samples:
                    sample_name = g.name
                    intensity = int_df.loc[i, sample_name]
                    int_list.append(intensity)
                average_int = sum(int_list) / len(int_list)
                group_df.loc[i, group] = average_int
                # group_df.loc[i, group] = '%.2E' % Decimal(average_int)

        group_df['max_value'] = group_df.max(axis=1)

        return group_df


    def get_list_view_column_names(self, column_names):
        """
        A method to return user friendly column names given the group name. This also returns a heading for the maximum value
        This is created for the list view but could be modified for general use.
        :param column_names:This is the names of the groups.
        :return: Dictionary with group: user-friendly column name
        """
        group_name_dict = {}
        groups = column_names

        for g in groups:
            if g == 'max_value':
                group_name_dict[g] = "Max" + " " + "Value"
            elif g == 'Metabolite':
                group_name_dict[g] = g
            else:
                sample = Sample.objects.filter(group=g)[0]  # Get the first sample of this group.
                tissue = sample.tissue
                ls = sample.life_stage
                group_name_dict[g] = tissue + " " + "(" + ls + ")"

        return group_name_dict

    def get_single_cmpd_df(self):
        """
        This method returns a dataframe of the grouped peaks (average values) without any duplicate compounds.
        :return:
        """
        logger.info("Getting a DF of peaks containing with no duplicate compounds")
        self.int_df.replace(0, np.nan, inplace=True)

        # KMcL: TEMP: Change zero values to Nan here as a temporary measure - should be done upstream in PiMP.

        group_df = self.get_group_df(self.int_df)

        peak_sids = list(self.int_df.index.values)
        compound_names = self.int_df['Metabolite'].tolist()
        group_df.insert(0, 'Metabolite', compound_names)


        duplicate_compounds = [item for item, count in collections.Counter(compound_names).items() if count > 1]
        sec_ids_to_delete = []

        for dc in duplicate_compounds:
            dup_peaks = Peak.objects.filter(cmpd_name=dc)
            max_values_dict = {}
            for dp in dup_peaks:
                max_value = group_df.loc[dp.psec_id]['max_value']
                max_values_dict[dp.psec_id] = max_value
            # logger.debug(max_values_dict)

            # Get the key with the maximum value to keep
            to_keep = max(max_values_dict.items(), key=operator.itemgetter(1))[0]
            keys = (list(max_values_dict.keys()))
            keys.remove(to_keep)
            # logger.debug("The smaller peaks are being deleted %s", str(keys))
            for k in keys:
                sec_ids_to_delete.append(k)

        non_dup_ids = [sid for sid in peak_sids if sid not in sec_ids_to_delete]
        # Get a DF of cmpd_name, Group_columns and average values??
        non_dup_names_df = group_df.loc[non_dup_ids]

        logger.info("The number of (non-duplicate) compounds being returned is %s", non_dup_names_df.shape[0])

        return non_dup_names_df


    def get_compound_details(self, peak_id):
        """
        Method to return the compound parameters associated with a peak.
        :param peak_id: Id of the peak that you want the compound details for
        :return: A dictionary with compound details of the peak
        """
        peak = Peak.objects.get(psec_id=peak_id)

        compound_details = {'hmdb_id':peak.get_hmdb_id(), 'kegg_id':peak.get_kegg_id(),'mz':peak.m_z, 'mass': peak.neutral_mass,
                            'rt': peak.rt, 'formula': peak.cmpd_formula, 'adduct': peak.adduct, 'name': peak.cmpd_name }

        return compound_details