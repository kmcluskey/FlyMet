from IPython.display import display
from difflib import SequenceMatcher
from met_explore.helpers import get_filename_from_string

import pandas as pd
import numpy as np
import logging
import json


logger = logging.getLogger(__name__)

PROTON = 1.007276
K = 39.0983
Na = 22.98977
ACN = 41.0524
NAME_MATCH_SIG = 0.5
MASS_TOL = 0.1
RT_TOL = 5
EXT_RT_TOL = 20 #Extended RT tolerance as the peak picking seemed odd


# A class to select the peaks required to use in further analysis

class PeakSelector(object):

    # The constructor just in a peak_json file from PiMP
    # and an intensity json file from Pimp (samples [col], peaks [rows], intensities [cells]
    def __init__(self, peak_json_file, intensity_json_file):

        self.peak_json_file = peak_json_file
        self.intensity_json_file = intensity_json_file
        # Taking the expected RT from the Stds_ALL.csv file and multipling by 60 - hopefully can
        # read this directly from a CSV file in the future

        self.std_temp_dict = {"Maltose": 775.8, "sucrose": 742.2, "trans-4-Hydroxy-L-proline":720.6, "5-Aminolevulinate":696.0}


    def get_selected_df(self, peak_details_df):

        """
        :param peak_details_df:
        :return: selected_df
        :return: unique_sec_ids

        """

        # Filter on adduct types
        selected_adducts = (peak_details_df['adduct'] == 'M+H') | (peak_details_df['adduct'] == 'M-H')
        f_adducts = peak_details_df[selected_adducts].copy()

        # Select peaks that have been identified and/or has a FrAnk annotation associated with them
        with_annot = (f_adducts['frank_annot'].notnull()) | (f_adducts['identified'] == 'True')
        with_annots_df = f_adducts[with_annot].copy()

        # This DF contains peaks that are (identified &| fannotated) & (M+H | M-H)
        selected_df = self.add_neutral_masses(with_annots_df)
        unique_sec_ids = selected_df['sec_id'].unique()

        return selected_df, unique_sec_ids



    def construct_all_peak_df(self):

        """
        A method to return a DF similar to the one produced by PiMP but for each peak, each unique compound (cmpd_id) is
        given a single row and the compound identifiers are collected.

        :return: all_peak_df- a DF consisting of all peaks with each compound represented by a single row.
        """

        peak_details_df = pd.read_json(self.peak_json_file)

        file_name = get_filename_from_string(self.peak_json_file)

        print ("The filename is:", file_name)

        try:
            all_peak_df = pd.read_pickle("./data/"+file_name+".pkl") #KMCL - this file should be named after the input files so not to repeat.

            print ("WE have the DF", all_peak_df.head())

        except FileNotFoundError:
            print('constructing all_peak_df')
            all_peaks = self.add_neutral_masses(peak_details_df)

            headers = list(all_peaks.columns.values)
            all_peak_df = pd.DataFrame(columns=headers)
            all_unique_sec_ids = all_peaks['sec_id'].unique()

            print ("Constructing the all peak DF")

            # For each unique peak just
            for sid in all_unique_sec_ids:

                sid_df = all_peaks[all_peaks.sec_id == sid]
                # print("The single SID DF is", sid_df)
                unique_cmpd_ids = sid_df['cmpd_id'].unique()

                # For each of the unique compounds add a row to the DF
                for cmpd_id in unique_cmpd_ids:
                    new_row = self.get_peak_by_cmpd_id(sid_df, cmpd_id)
                    all_peak_df = all_peak_df.append(new_row)

            logger.info("Picking the DF to store at ./data/all_peak_df.pkl")

            try:
                all_peak_df.to_pickle("./data/+"+file_name+".pkl")
            except Exception as e:
                logger.error("Pickle didn't work because of %s ", e)
                pass

        print("There are", all_peak_df['sec_id'].nunique(), "unique peaks out of", all_peak_df.shape[0], "rows added to the all_peak_df")


        return all_peak_df


    def construct_high_confidence_peak_df(self, selected_df, unique_sec_ids):
        """
        A method to return a DF of unique peaks - based on the reliability of the compound.
        i.e a single row is chosen for each peak.
        If the each compound/adduct combination is stored once so some unique peaks are possible removed.

        :return: peak_df- a DF of unique peak IDs
        """

        headers = list(selected_df.columns.values)
        peak_df = pd.DataFrame(columns=headers)

        print ("Constructing the High Conf peak DF")

        for sid in unique_sec_ids:
            # Collect a single sec_id into a DF
            sid_df = selected_df[selected_df.sec_id == sid]

            logger.debug("The single SID DF is %S", sid_df)
            # If the peak has an identified compound then keep that
            identified_df = sid_df[sid_df.identified == 'True']
            logger.debug("The identified df is: %S ", identified_df)
            new_row = None
            # If some of the rows have compounds that have identified=True
            if not identified_df.empty:

                # Check if there are more than one standard compounds for this sid
                standard_cmpds = sid_df[sid_df.db == 'stds_db']
                num_std_cmpds = standard_cmpds.shape[0]

                # If there is only one standard compound add this to the peak DF and collect identifiers.
                if (num_std_cmpds == 1):
                    print("we have only one standard compound")
                    cmpd_id = sid_df[sid_df.db == "stds_db"]['cmpd_id'].values[0]
                    new_row = self.get_peak_by_cmpd_id(sid_df, cmpd_id)

                    # Here we have the senario that more that 1 standard compound has been identified and we
                # want to select a standard compound if possible
                if (num_std_cmpds > 1):
                    print("the number of standard compounds for sid is", sid, "is", num_std_cmpds)
                    new_row = self.select_standard_cmpd(sid_df, standard_cmpds)

                # If a new_row has been returned for this SID - add it to the peak df
                if new_row is not None:

                    print("we are adding the row for sid", sid)
                    print(pd.DataFrame(new_row).T)
                    peak_df = peak_df.append(new_row)

                    # If the new_row has not been determined for this SID
                else:

                    unique_cmpd_ids = sid_df['cmpd_id'].unique()

                    # For each unique compound id add a row to the peak df, this will produce duplicates for later
                    for ucid in unique_cmpd_ids:
                        new_row = self.get_peak_by_cmpd_id(sid_df, ucid)
                        print("we are now adding the row: for sid", sid)
                        print(pd.DataFrame(new_row).T)
                        peak_df = peak_df.append(new_row)

                        # Else nothing identified so look at the fragmentation data.
            else:
                # Get all the rows for this secondary ID
                print("nothing identified here so get best match FrAnk compound")
                new_row = self.select_on_frank(sid_df)
                print("we are adding the row: for sid", sid)
                print(pd.DataFrame(new_row).T)
                peak_df = peak_df.append(new_row)


        # Quite a few duplicates still exist from the Standard compound identification.
        # These methods attempt to tackle this in a sensible manner.

        peak_df = self.remove_duplicates_on_mass_rt(peak_df)
        peak_df = self.remove_double_duplicates(peak_df)
        peak_df = self.remove_duplicate_on_name_adduct(peak_df)
        peak_df = self.remove_duplicates_on_rt(peak_df)

        logger.info("There are %d unique peaks out of %d highly selected rows added", peak_df['sec_id'].nunique(), peak_df.shape[0])

        return peak_df


    def construct_int_df(self, peak_df):

        """
        A method to return a sample/intensity DF for each peak in the peak_df
        :param peak_df: All of the peaks we want to sample intensities for
        :return: int_details_df - a DF filtered to contain only the peaks in the peak_df
        :return: pids_sids_dict - a dictionary of the pimp ids / pimp sec_ids for the peaks used.

        """
        int_details_df =  pd.read_json(self.intensity_json_file)

        ### Get a dictionary pf pids:sec_id from the final peak df.
        pids_sids_dict = {}

        for index, row in peak_df.iterrows():
            pids_sids_dict[row['pid']] = row['sec_id']

        for index, row in int_details_df.iterrows():
            if index not in pids_sids_dict:
                int_details_df = int_details_df.drop(index)

        #Add the sec_ids to the dictionary file
        print("returning an intensity DF with", int_details_df.shape[0], "peaks")

        return int_details_df, pids_sids_dict


    def remove_duplicates_on_mass_rt(self, peak_df):
        """
        Take the originally constructed DF and look for sec_ids that have more than one compound associated with them
        First look for the matching name/opposite-adduct pairs based on RT and neutral mass.
        If one is found that matches, delete the other duplicate peaks.
        """
        duplicate_df = peak_df[peak_df.sec_id.duplicated()]
        dup_ids = duplicate_df['sec_id'].values
        print("dup_ids are ", dup_ids)

        for dupid in dup_ids:
            dup_peaks = peak_df[peak_df.sec_id == dupid]
            print("duplicate peaks are: ")
            display(dup_peaks)

            #     Assuming that all of the data for these duplicate peaks are the same, take the first value.
            neutral_mass = dup_peaks['neutral_mass'].iloc[0]
            rt = dup_peaks['rt'].iloc[0]
            adduct = dup_peaks['adduct'].iloc[0]

            min_mass = neutral_mass - MASS_TOL
            max_mass = neutral_mass + MASS_TOL

            min_rt = rt - EXT_RT_TOL
            max_rt = rt + EXT_RT_TOL

            mass_match = peak_df['neutral_mass'].between(min_mass, max_mass, inclusive=True)
            rt_match = peak_df['rt'].between(min_rt, max_rt, inclusive=True)
            no_duplicates = peak_df['sec_id'] != dupid

            keep_index = {}
            dup_indexes = list(dup_peaks.index.values)

            matching_cmpd_df = peak_df[mass_match & rt_match & no_duplicates]

            # If we have stored another peak within a particular neutral_mass and rt tolerance.

            if matching_cmpd_df.index.any():

                print("Other single peaks that match the duplicate peak on mass and rt are:")
                display(matching_cmpd_df)

                #   Peak ids for the peaks that match the duplicate peak.
                match_sec_ids = matching_cmpd_df['sec_id'].values

                for m in match_sec_ids:

                    match_cmpd = matching_cmpd_df[matching_cmpd_df.sec_id == m]
                    match_name = match_cmpd['compound'].iloc[0]
                    match_adduct = match_cmpd['adduct'].iloc[0]

                    for index, row in dup_peaks.iterrows():

                        pimp_cmpd_name = row['compound']

                        if (pimp_cmpd_name == match_name) and (match_adduct != adduct):
                            print("names are the same and the adducts are different")
                            print("keeping this:")
                            display(dup_peaks[dup_peaks['compound'] == pimp_cmpd_name])
                            abs_rtdif = (match_cmpd['rt'] - rt).abs().iloc[0]
                            keep_index[index] = abs_rtdif

                            #  If we have found one peak that we should keep, delete the others.

                print("keep_index", keep_index)

                if len(keep_index) == 1:
                    print("There is only one duplicate peak compound highlighted and therefore deleting others")
                    keys = list(keep_index.keys())
                    keep = keys[0]
                    peak_df = self.drop_duplicates(dup_indexes, keep, peak_df)


                elif len(keep_index) > 1:
                    print("More than one compound in mass/rt range and therefore keeping the one with the smallest absolute difference from the RT")
                    min_index = min(keep_index, key=keep_index.get)
                    keep = min_index
                    peak_df = self.drop_duplicates(dup_indexes, keep, peak_df)

        return peak_df

    def remove_double_duplicates(self, peak_df):

        """
        If we have more than one peak with matching duplicate compounds
        Keep the compound with the closest RT to that found in the standard csv file (run with the mass spec)
        Delete the other compound(s) from the peak
        """
        print ("Checking for peaks with duplicate compounds that match (compound name/adduct) other duplicate peaks")
        duplicate_df = peak_df[peak_df.sec_id.duplicated()]
        dup_ids = duplicate_df['sec_id'].values

        duplicates = peak_df['sec_id'].isin(dup_ids)
        all_duplicates = peak_df[duplicates]

        # if there are any duplicate names in the duplicate peaks then we have
        if any(all_duplicates['compound'].duplicated()):

            # Get the compound names
            dup_compounds = all_duplicates[all_duplicates['compound'].duplicated(keep=False)]
            print ("`Duplicate peaks with duplicate compounds")
            display(dup_compounds)
            sids = list(np.unique(dup_compounds['sec_id'].values))

            df_to_check = peak_df[peak_df['sec_id'].isin(sids)]
            name_rt_dict = {}

            for index, row in df_to_check.iterrows():
                name_rt_dict[index] = [row['compound'], row['rt']]

            print(name_rt_dict)

            keep_index = self.get_closest_rt_match(name_rt_dict)

            sec_id_chosen = peak_df.loc[keep_index, 'sec_id']

            dup_peaks = peak_df[peak_df["sec_id"] == sec_id_chosen]
            dup_indexes = list(dup_peaks.index.values)

            peak_df = self.drop_duplicates(dup_indexes, keep_index, peak_df)

        return peak_df


    def remove_duplicate_on_name_adduct(self, peak_df):

        """
        If any of the compounds in the duplicate peaks match on name and adduct to others stored then delete them
        """

        duplicate_df = peak_df[peak_df.sec_id.duplicated()]
        dup_ids = duplicate_df['sec_id'].values

        print("Looking for compounds that have already been chosen with the same name and adduct")

        duplicates = peak_df['sec_id'].isin(dup_ids)
        all_duplicates = peak_df[duplicates]
        print ("current duplicates are:")
        display(all_duplicates)

        # Check if there are any of the same compounds already stored.

        # For each secondary_id
        for dupid in dup_ids:

            duplicates = peak_df[peak_df['sec_id'] == dupid]

            for index, row in duplicates.iterrows():

                name = row['compound']
                adduct = row['adduct']

                name_match = peak_df['compound'] == name
                adduct_match = peak_df['adduct'] == adduct
                no_duplicates = peak_df['sec_id'] != dupid

                matching_rows = peak_df[name_match & adduct_match & no_duplicates]

                if matching_rows.index.any():
                    print("we have aready stored this compound/adduct ratio so dropping this")
                    display(matching_rows)
                    peak_df = peak_df.drop(index)
                else:
                    print("no matching row for ", name, adduct)

        return peak_df


    def remove_duplicates_on_rt(self, peak_df):
        """
        For a peak with duplicate compounds - keep the one with the closest RT to the STD DB expected value.
        Delete the others.
        """
        duplicate_df = peak_df[peak_df['sec_id'].duplicated(keep=False)]
        print ("the duplicates at this stage are: ")
        display(duplicate_df)
        dup_ids = set(duplicate_df['sec_id'].values)
        name_rt_dict = {}

        for dupid in dup_ids:

            name_rt_dict = {}
            dup_indexes = []
            dup_peaks = peak_df[peak_df.sec_id == dupid]

            for index, row in dup_peaks.iterrows():
                dup_indexes.append(index)
                name_rt_dict[index] = [row['compound'], row['rt']]


            keep_index = self.get_closest_rt_match(name_rt_dict)
            peak_df = self.drop_duplicates(dup_indexes, keep_index, peak_df)

        return peak_df


    def get_closest_rt_match(self, name_rt_dict):
        """
        For a peak with duplicate compounds - keep the one with the closest RT to the STD DB expected value.
        :param: A dictionary the names and RT of the compounds
        :returns: The index of the compound that should be kept i.e. the closest match.
       """
        abs_dic = {}
        for index, name_rt in name_rt_dict.items():
            dup_name = name_rt[0]
            dup_rt = name_rt[1]
            for name, rt in self.std_temp_dict.items():
                if name == dup_name:
                    abs_value = abs(dup_rt - rt)
                    abs_dic[index] = abs_value

        logger.info("The abs dict is, %s ", abs_dic)
        keep_index = min(abs_dic, key=lambda x: abs_dic.get(x))
        print("The keep_index is", keep_index)  # Return this and then use it as below.

        return keep_index


    def drop_duplicates(self, dup_indexes, keep_index, peak_df):
        """
        A method to drop rows from a DF given the index to keep and those of all the duplicate rows for a peak.
        :param: dup_indexes - indices of the rows of a peak with duplicate compounds
        :param: keep_index - the index of the row that we want to keep

        """
        dup_indexes.remove(keep_index)

        for index_to_drop in dup_indexes:
            print("dropping this")
            display(peak_df.loc[[index_to_drop]])
            peak_df = peak_df.drop(index_to_drop)

        return peak_df


    def select_standard_cmpd(self, sid_df, standard_cmpds):
        """
        Choose a standard compound based on the one which matches the name of the FrAnk annotation most closely.
        :param sid_df: a dataframe of the rows of the peaks for a single peak ID
        :param standard_cmpds: A dataframe for the peak containing only the standard compounds
        :return: A new row for the final df based on FrAnk or None (if FrAnk None)
        """

        print ("selecting standard compound")
        new_row = None
        display(standard_cmpds)
        name_match_dic = {}
        # For each of the standard compounds identified for the peak
        for i in standard_cmpds['cmpd_id'].unique():
            pimp_cmpd_name = standard_cmpds[standard_cmpds.cmpd_id == i]['compound'].iloc[0]
            annotation = standard_cmpds['frank_annot'].values[0]  # Get the value in the cell

            # If there is a FrAnK annotation get the best name match
            if (annotation is not None):

                frank_cmpd_name = annotation['frank_cmpd_name']
                m = SequenceMatcher(None, frank_cmpd_name, pimp_cmpd_name)
                name_match_dic[pimp_cmpd_name] = m.ratio()

                print(name_match_dic)
                max_value = max(name_match_dic.values())  # maximum value
                max_keys = [k for k, v in name_match_dic.items() if v == max_value]
                max_key = max_keys[0]
                print("max_key to grab row", max_key)

                new_row = standard_cmpds[standard_cmpds['compound'] == max_key].iloc[0]

                ucid = new_row['cmpd_id']
                cmpd_rows_df = sid_df[sid_df.cmpd_id == ucid]
                identifiers = self.get_all_identifiers(cmpd_rows_df)
                new_row.at['identifier'] = identifiers
        print ("returning new row: ", new_row)
        return new_row

    # Choose a compound based on how closely it matches the name of the FrAnK annotation. If it is less than 50% return
    # the FrAnk details instead

    def select_on_frank(self, sid_df):
        """
        :param sid_df: a dataframe of the rows of the peaks for a single peak ID
        :return: A new row for the peak df based on FrAnk (should not be None)
        """
        new_row = None
        name_match_dic = {}
        compound_names = sid_df['compound'].values
        single_annot = sid_df['frank_annot'].values[0]

        for pimp_cmpd_name in compound_names:
            # Find the best fit for to frank.
            frank_cmpd_name = single_annot['frank_cmpd_name']
            m = SequenceMatcher(None, frank_cmpd_name, pimp_cmpd_name)
            name_match_dic[pimp_cmpd_name] = m.ratio()

        if name_match_dic:
            print(name_match_dic)
            max_value = max(name_match_dic.values())  # maximum value
            max_keys = [k for k, v in name_match_dic.items() if v == max_value]
            max_key = max_keys[0]

            # if (max_value >= 0.5):
            print("max_key to grab row", max_key)

            new_row = sid_df[sid_df['compound'] == max_key].iloc[0]
            ucid = new_row['cmpd_id']
            cmpd_rows_df = sid_df[sid_df.cmpd_id == ucid]
            identifiers = self.get_all_identifiers(cmpd_rows_df)
            new_row.at['identifier'] = identifiers

            # If the match is less than 50% just take the frank annotation instead.
            # if (max_value < 0.5):
            #     print("max_value is < 0.5 (", max_value, ") and so taking frank annot")
            #
                # new_row = self.get_frank_annot(sid_df)

        print("The FrAnK probability score is", single_annot['probability'])

        return new_row

    def get_frank_annot(self, sid_df):
        """
        :param sid_df: Dataframe containing all rows for a single peak (sid, secondary id)
        :return: A new row of the dataframe based on the FrAnk compound (instead of the PiMP one)
        """
        new_row = None
        frank_annots = sid_df['frank_annot']
        single_annot = frank_annots.iloc[0]

        if any(single_annot):

            print("Collecting the compound info from", single_annot)

            new_row = sid_df.iloc[0]
            new_row.at['compound'] = single_annot['frank_cmpd_name']

            # Get all the frAnk identifiers for a single PiMP compound (could be one).
            identifiers = []
            identifier_keys = ['inchikey', 'cas_code', 'hmdb_id']
            for i in identifier_keys:
                identifiers.append(single_annot[i])
            new_row.at['identifier'] = identifiers

        return new_row


    def get_peak_by_cmpd_id(self, sid_df, ucid):
        """
        A method to return a row for an identified peak given the chosen compound id
        :param: A df containing a set of peaks with a single ID and the unique cmpd ID
        :returns: A new_row (peak) to be added to the peak df.
        """
        # new_row = None  # Clear the new row at this stage
        cmpd_rows_df = sid_df[sid_df.cmpd_id == ucid]
        identifiers = self.get_all_identifiers(cmpd_rows_df)
        print("The returned identifiers are ", identifiers)
        cmpd_id = cmpd_rows_df['cmpd_id'] == ucid

        # Take the row with std_db just to remember this compound was identified.
        db = cmpd_rows_df['db'] == 'stds_db' #If the compound was identified
        print ("DB", db)
        if db.any():
            new_row = cmpd_rows_df[cmpd_id & db].iloc[0]
        else:
            new_row = cmpd_rows_df[cmpd_id].iloc[0]

        new_row.at['identifier'] = identifiers

        print('Returning new_row by cmpd_id')

        return new_row


    def get_all_identifiers(self, cmpd_rows_df):

        """ A method to return a list of identifiers for an identified
            :param A df containing a unique 'pimp' compound
            :returns: A list of identifiers relating to the compound
        """

        num_rows = cmpd_rows_df.shape[0]
        # Get all the identifiers for a single PiMP compound (could be one but want this as list).
        identifiers = []
        for i in range(0, (num_rows)):
            new_id = cmpd_rows_df.iloc[i]['identifier']
            for n in new_id:
                identifiers.append(n) #So we don't end up with a list of lists

            # Take one of the rows for this compound, add identifiers and save in the final df.

        return identifiers

    def add_neutral_masses(self, df):

        """ A method to add neutral masses to a DF
            Params: The df containing M+H or M-H adducts (no other adducts)
            Returns: A dataframe with the neutral masses added.
        """
        logger.info("Adding neutral masses to the peaks")

        masses = df['mass'].values
        adducts = df['adduct'].values

        neutral_masses = []
        joint_list = [masses, adducts]

        mass_adducts = list(zip(*joint_list))
        for ma in mass_adducts:
            mass = ma[0]
            adduct = ma[1]
            neutral_mass = self.get_neutral_mass(mass, adduct)
            neutral_masses.append(neutral_mass)

        df['neutral_mass'] = np.asarray(neutral_masses)

        return df

    def get_neutral_mass(self, mass, adduct):

        """
        Small function to return a neutral mass given the m/z and the adduct.
        :param mass: m/z of the adduct
        :param adduct: type of adduct - only M+H, M-H currently accepted
        :return: The neutral mass np.float
        """
        neutral_mass = None
        if adduct == 'M+H':
            neutral_mass = mass - PROTON
        elif adduct == 'M-H':
            neutral_mass = mass + PROTON
        elif adduct =='M+Na':
            neutral_mass = mass - Na
        elif adduct == 'M+ACN+Na':
            neutral_mass = mass - ACN - Na
        elif adduct == 'M+ACN+H':
            neutral_mass = mass - ACN - PROTON
        elif adduct == 'M+K':
            neutral_mass = mass - K
        elif adduct == 'M-K':
            neutral_mass = mass + K
        elif adduct == 'M-Na':
            neutral_mass = mass + Na
        else:
            logger.warning("This is not the correct type of adduct: %s and therefor skipping", adduct)
            return

        return neutral_mass