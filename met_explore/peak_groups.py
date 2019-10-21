import logging
from met_explore.models import *
from met_explore.peak_selection import PeakSelector
import pandas as pd
import numpy as np
import itertools

from met_explore.compound_selection import CompoundSelector
from IPython.display import display, HTML
from decimal import *

logger = logging.getLogger(__name__)

NAME_MATCH_SIG = 0.5
MASS_TOL = Decimal(0.01)
RT_TOL = 5


# Methods to select groups of peaks

class PeakGroups(object):

    """
    A class to Generate groups of peaks associated with a compound given the cmpd_id
    """

    def __init__(self, cmpd_id):
        # Get all of the annotations associated with this compound
        self.annotations = Annotation.objects.filter(compound_id=cmpd_id)

        self.peak_dict = {}
        for a in self.annotations:
            self.peak_dict[int(a.peak_id)]= {"adduct":a.adduct, "nm":a.neutral_mass, "rt":a.peak.rt, "conf":a.confidence}
        self.peak_list = [(int(a.peak.id), a.adduct, a.neutral_mass, a.peak.rt, a.confidence) for a in self.annotations]
        self.no_peaks = len(self.peak_list)

        logger.info ("Getting groups of peaks for cmpd with ID %s", cmpd_id)


    def get_peak_groups(self):

        """
        This method will take in a cmpd ID and return all the peaks associated with the compound in groups.
        :param self:
        :param cmpd: The compound for which the peak groups are required
        :return: adduct_group_list: All of peak groups associated with that compound as a list of dataframes where each DF is a peak group

        """

        # Looking at the compound peaks iterate over collecting peaks that are near in RT/nm
        initial_peak_groups =self.get_close_peaks()
        # Single peaks are peaks that are not founf to have other nm/RT peaks
        single_peaks_df = self.get_single_peaks(initial_peak_groups)

        # If there are an initial group then collect them into adduct group lists
        if len(initial_peak_groups) > 1:
            #Similar to a network, collect all of the peaks that are linked to one another
            collected_peaks = self.collect_connected_peaks(initial_peak_groups)
            # For the collected peaks split into adduct groups so that there are no duplicate adducts in a group.
            adduct_groups_list = self.select_adduct_groups(collected_peaks)
        else: #Initialise an empty list for the single groups.
            adduct_groups_list=[]
        #Add single peaks to the groups

        for index, row in single_peaks_df.iterrows():
            adduct_groups_list.append(pd.DataFrame(single_peaks_df.loc[index]).transpose())

        # for a in adduct_groups_list:
        #     print ("AAAA ", a)
        #     print (type(a))
        #     for index, row in a.iterrows():
        #         print ("ROW ", type(row.peak_id))
        #
        return adduct_groups_list

        #Make sure we check that we start and end with the same number of peaks.


    def get_close_peaks(self):
        """
        :return: This returns a dictionary where the k is a peak and v is a list of peaks and
        they are all grouped through mass and retention time tolerance
        """
        peak_groups = {}
        # This iterloops.combinations - starts at one end of the list and compares all other items without duplicating.
        # So one we find all the other peaks that match a
        for a, b in itertools.combinations(self.peak_list, 2):  # Compare all combinations of the list with itself.
            pk, add, nm, rt, conf = a
            p, a, n, r, c = b
            # If the retention time is within a specific tolerance level
            if (rt - RT_TOL <= r <= rt + RT_TOL):
                # Check RT as all NM should be the same.
                if (nm - MASS_TOL <= n <= nm + MASS_TOL):
                    if not pk in peak_groups:
                        peak_groups[pk] = [p]
                    else:
                        # The key exists
                        peak_groups[pk].append(p)
        logger.info("Peaks within an RT/nm tolerance of one another are: %s ", peak_groups)
        return peak_groups


    def get_single_peaks(self, peak_groups):
        """
        # For peaks that did not fall within the nm/RT tolerance range, collect these as single/individual peaks.
        :param peak_groups: A dictionary of peaks (as keys and values) that contain peaks that have mass or RT matches.
        :return: A list of peaks without Neutral mass or retention time masses.
        """
        peak_ids = (list(self.peak_dict.keys()))

        single_peaks = []

        for p in peak_ids:
            not_in_keys = not (p in peak_groups.keys())
            not_in_values = not (any(p in sublist for sublist in peak_groups.values()))
            if not_in_keys and not_in_values:
                # Add a none to the list
                single_peaks.append(p)

        logger.info("Peaks that don't match any others with a RT/nm tolerance: %s ", single_peaks)

        single_peak_details = [self.peak_dict[k] for k in single_peaks]
        single_peaks_df = pd.DataFrame(single_peak_details, dtype=object)
        single_peaks_df.insert(loc=0, column='peak_id', value=single_peaks)

        single_peaks_df = single_peaks_df.astype(object)


        return single_peaks_df


    def collect_connected_peaks(self, peak_groups):
        """
        This method aims to collect all of the peaks connected to each other - this means that the overall RT tolerance can be much greater that
        what is originally set.
        :return: peak_groups - a dictionary where all the peaks are collected into connected groups.
        e.g. if A is related to B and B to C and D then A is related to B, C and D.
        """
        logger.info("Collecting all of the peaks connected to one another")
        # #This method gathers all matching peaks into a single dictionary entry where the key and the values are all within a nm
        # # and RT tolecrance,
        for k, v in list(peak_groups.items()):
            # print("for this key and values ", k, v)
            for val in v:  # Check all of the peaks associated with this one
                # If this is a key for another group in the list
                # print ("looking at val ", val)
                if val in peak_groups.keys():
                    for peak in peak_groups[val]:
                        # For each value in the dictionary that has val as a key//
                        # Check if the values match those in the orginal k,v set and if not add them.
                        if (not peak in peak_groups[k]):  # If one of these peaks is not in the original peak list
                            peak_groups[k].append(peak)  # Add the value to the dictionary

                # If the value is found as a value in another list
                if any(val in sublist for sublist in peak_groups.values()):
                    # Get the keys that contain this value
                    keys = self.get_keys_by_value(peak_groups, val)
                    for ky in keys:
                        # If the key is greater than the key we have been working on (working in key-size order)
                        if ky > k:
                            #  If this key is not in the orignal group - add it
                            if (not ky in peak_groups[k]):
                                peak_groups[k].append(ky)
                            for peak in peak_groups[ky]:
                                # Check if the values match those in the orginal k,v set and if not add them.
                                if (not peak in peak_groups[k]):  # If one of these peaks is not in the original peak list
                                    peak_groups[k].append(peak)  # Add the value to the dictionary
                                # Remove the key (ky) as we have added all the peaks to another key
                                peak_groups.pop(ky, None)

                # print("popping peak ", val)
                peak_groups.pop(val, None)  # Delete the key if it exist (or return None if it doesnt')

        logger.info("Returning a collection of connected peak groups %s", peak_groups)

        return peak_groups



    def select_adduct_groups(self, peak_groups):
        """

        :param peak_groups: A dictionary of peak_groups (k,[v,v,] is a group) and select the most closely related adducts to return.
        :return: A list of dataframes, each containing groups without duplicate adducts
        """

        # For each group of peaks - pick a sensible peak_group
        peak_df_list = []
        for k, v in peak_groups.items():
            keys_to_select = [k]

            # Get the dictionary peaks for this group
            for values in v:
                keys_to_select.append(values)

            peak_details = [self.peak_dict[k] for k in keys_to_select]
            peak_df = pd.DataFrame(peak_details, dtype=object)

            peak_df.insert(loc=0, column='peak_id', value=keys_to_select)
            peak_df = peak_df.astype(object) #Remove int64 at this point

            logger.info("THE RELATED ADDUCT DF IS %s", peak_df)

            single_adduct_df, leftover_peaks_df = self.collect_single_adducts(peak_df)
            peak_df_list.append(single_adduct_df)

            while (leftover_peaks_df is not None) and (not leftover_peaks_df.empty):
                single_adduct_df, leftover_peaks_df = self.collect_single_adducts(leftover_peaks_df)
                peak_df_list.append(single_adduct_df)

        for p in peak_df_list:
            logger.info("returning the group split in to %s ", p)
        return peak_df_list

    def collect_single_adducts(self, peak_df):
        """
        :param peak_df: A collection of peaks within a RT/NM window but that may have duplicate adducts.
        :return: A group of peaks with single adducts and the left over peaks from the starting group.
        """
        all_adducts = set(peak_df.adduct.values)
        leftover_peaks_df = None
        saved_peaks = None #Save single adduct peaks if they are not close in RT to other single adduct peaks

        if (peak_df.shape[0] == len(all_adducts)):
            single_adduct_df = peak_df

        else:

            # If there are any non-duplicate adducts add them to the new DF
            single_adduct_df = peak_df.drop_duplicates(subset=['adduct'], keep=False)
            # If there are no single adducts we just have duplicates.
            # If these are exactly the same delete one and if not split into two groups.
            if single_adduct_df.shape[0] > 1:
                #check if the rt are within a sensible toterance
                remove_list = []
                diff_dict = {}  # Key = index, value = diff in RT from the 0 index

                for i, r in single_adduct_df.iterrows():
                    # Save the difference in retention time between the first row and all other rows.
                    diff_dict[i] = abs(single_adduct_df.iloc[0].rt - r.rt)

                for index, diff in diff_dict.items():
                    if diff > RT_TOL:
                        remove_list.append(index)

                saved_peaks = single_adduct_df.loc[remove_list]
                if saved_peaks.empty:
                    saved_peaks = None

                single_adduct_df = single_adduct_df.drop(remove_list)


            dup_adduct_rows = peak_df[
                peak_df['adduct'].duplicated(keep=False)]  # keep = false - mark all duplicates as true
            dup_adducts = set(dup_adduct_rows.adduct.values)

            logger.info("THE duplicate adduct rows are %s ", dup_adduct_rows)

            for adduct in dup_adducts:

                single_dup_adduct_df = peak_df[peak_df['adduct'] == adduct]
                keep_index = self.get_closest_adduct(single_dup_adduct_df, single_adduct_df)

                if len(keep_index) > 1:
                    logger.warning("DUPLICATES")

                to_keep = peak_df.loc[keep_index]
                single_adduct_df = single_adduct_df.append(to_keep)
                peak_df.drop(keep_index)

            leftover_peaks_df = peak_df.drop(single_adduct_df.index)

            if saved_peaks is not None:
                if (leftover_peaks_df is not None) and (not leftover_peaks_df.empty): #If we have leftover peaks add to that.
                    leftover_peaks_df = leftover_peaks_df + saved_peaks
                else:
                    # print ("leftover is empty saving saved_peals")
                    leftover_peaks_df = saved_peaks

        # print ("LEFTOVER PEAKS ", leftover_peaks_df)
        # if leftover_peaks_df.empty:
        #     print ("in this empty loop")
        #     leftover_peaks_df=None

        logger.info("returning the single peak df %s and the leftover peaks %s", single_adduct_df, leftover_peaks_df)
        return single_adduct_df, leftover_peaks_df

    # Which one is closest in value to other adducts?

    #####KMCL - we need to remove identical peaks from our peak groups - maybe when we are setting up the dictionary...
    def get_closest_adduct(self, dup_adduct_rows, single_adduct_df):
        """

        :param dup_adduct_rows: A DF containing duplicate adducts for this group,
        :param single_adduct_df: The peaks for single adducts for this group. which we want to test the adduct rows against - i.e. which are nearest in RT
        :return: closest index - A list of the indexes of the rows cloests to those in  the single_adduct df
        """
        closest_indexes =[]

        if single_adduct_df.empty:

            logger.info("No Single adducts to start the group")

            # If there are no single adducts we just have duplicates.
            # If these are exactly the same delete one and if not split into two groups.

            dup_all_params = dup_adduct_rows[dup_adduct_rows.duplicated(['nm', 'rt'], keep=False)]

            if dup_all_params.empty:  # None of the peaks are the same
                closest_indexes.append(dup_adduct_rows.index[0])  # Keep the first row - send the other back as leftover

            else:
                # print("WE HAVE DUPLICATE PEAKS!!!")
                closest_indexes.append(dup_adduct_rows.index.values) #Send back both peaks.

        else:
            min_rt_keys = self.return_min_difference(dup_adduct_rows, single_adduct_df, 'rt')
            # print ("THE Min RT keys are ", min_rt_keys)
            if len(min_rt_keys) >1: #If There is more that one peak with this RT - check the nm
                min_nm_keys = self.return_min_difference(dup_adduct_rows, single_adduct_df, 'nm')
                closest_indexes = min_nm_keys
            else:
                closest_indexes = min_rt_keys

        # print("returning the closest index ", closest_indexes)

        return closest_indexes


    def return_min_difference(self, dup_adduct_rows, single_adduct_df, param):
        """

        :param dup_adduct_rows: A df containing rows of duplicate adducts
        :param single_adduct_df: A df containing single adducts that the dup adducts should be close to
        :param param: The parameter to be matched against
        :return: The index/key of the closest match to the given parameter.
        """

        compare_df = pd.DataFrame(dtype=object)
        compare_dict = {}  # Compare dict has the DF index as the key

        for index, row in dup_adduct_rows.iterrows():
            compare_df[index] = abs(single_adduct_df[param] - row[param])

        for cname, cdata in compare_df.iteritems():
            compare_dict[cname] = cdata.sum()

        min_key = min(compare_dict, key=compare_dict.get)

        min_val = compare_dict[min_key]  # This gets the miniumum value
        min_keys = [k for k, v in compare_dict.items() if v == min_val]

        return min_keys


    def get_keys_by_value(self, peak_dict, value):
        """
        Method to return the keys of a dictionary that contain a specific value in this instant the value is in a list
        :param peak_dict: The disctionary to be searched
        :param value: The value to be found in the values list
        :return:  A list of keys containing the value being searched for
        """
        keys = peak_dict.keys()
        key_list = []
        for k in keys:
            values = peak_dict[k]
            for val in values:
                if val == value:
                    key_list.append(k)
        return key_list