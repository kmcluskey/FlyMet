import collections
import operator
import timeit
import traceback

import numpy as np
import pandas as pd
import itertools
from django.db.models import Q
from loguru import logger
from tqdm import tqdm
from bioservices.kegg import KEGG
from met_explore.helpers import get_samples_by_factor, get_samples_by_factors, get_group_names, \
    get_factor_type_from_analysis, get_factors_from_samples, get_control_from_case

k = KEGG()

from met_explore.models import Peak, SamplePeak, Sample, Compound, Annotation, CompoundDBDetails, DBNames, \
    AnalysisComparison, Analysis, Group, Factor

INTENSITY_FILE_NAME = 'current_int_df'
HC_INTENSITY_FILE_NAME = 'current_hc_int_df'


class CompoundSelector(object):
    '''
    A class that contains various methods for selecting compounds from the peak object
    '''

    def __init__(self):

        self.USER_DEF = 5  # User defined
        self.AUTO_I = 4  # Auto generated and identified
        self.AUTO_F = 3  # Auto generated by fragmentation

    def get_hc_int_df(self):
        """
        Grab the hc_int_df without reconstructing it.
        :return: int_df - A DF with only thr High confidence peaks.
        """

        try:
            int_df = pd.read_pickle("./data/" + HC_INTENSITY_FILE_NAME + ".pkl")
            logger.info("The file %s has been found" % HC_INTENSITY_FILE_NAME)

        except Exception as e:
            logger.info("The file %s has not been found" % HC_INTENSITY_FILE_NAME)
            raise e

        return int_df

    def construct_hc_int_df(self, high_conf_df):

        try:
            hc_int_df_concat = pd.read_pickle("./data/" + HC_INTENSITY_FILE_NAME + ".pkl")

            logger.info("The file %s has been found" % HC_INTENSITY_FILE_NAME)

        except FileNotFoundError:

            logger.info("The high conf int DF is being constructed")

            samples = Sample.objects.all()

            sec_ids = high_conf_df['sec_id'].values
            peaks = Peak.objects.filter(psec_id__in=sec_ids)

            df_index = [p.id for p in peaks]

            logger.debug(df_index)

            # These two df are kept separately and concatenated at the end to preserve the datatype for the intensities
            columns = [s.name for s in samples]

            cmpd_columns = ['cmpd_id', 'Metabolite']

            int_df = pd.DataFrame(index=df_index, columns=columns, dtype=float)
            cmpd_df = pd.DataFrame(index=df_index, columns=cmpd_columns)

            # KMcL this has to be used with the peak ids for any sense.
            for p in tqdm(peaks):

                logger.debug("working on peak: ", p)
                peak = high_conf_df[high_conf_df.sec_id == p.psec_id]
                cmpd_id = peak['cmpd_id'].values[0]
                chebi_id = peak['chebi_id'].values[0]

                logger.debug("The cmpd_id, chebi_id is %s %s" % (cmpd_id, chebi_id))
                # cmpd_name = peak['compound'].values[0]
                # cmpd_formula = peak.formula.values[0]
                # cmpd_ids = peak.identifier.values[0]

                cmpd = Compound.objects.get(pc_sec_id=cmpd_id, chebi_id=chebi_id)

                cmpd_df.at[p.id, 'cmpd_id'] = cmpd.id
                cmpd_df.at[p.id, 'Metabolite'] = cmpd.cmpd_name

                for c in columns:
                    sp = SamplePeak.objects.get(peak__id=p.id, sample__name=c)
                    int_df.at[p.id, c] = sp.intensity

            hc_int_df_concat = pd.concat([cmpd_df, int_df], axis=1, sort=False)

            try:
                hc_int_df_concat.to_pickle("./data/" + HC_INTENSITY_FILE_NAME + ".pkl")

            except Exception as e:
                logger.error("Pickle didn't work because of %s ", e)
                traceback.print_exc()
                pass

        logger.info("There are %d peaks and %d unique compounds" % (hc_int_df_concat.shape[0],
                                                                    len(hc_int_df_concat['cmpd_id'].unique())))

        return hc_int_df_concat

    def construct_cmpd_intensity_df(self):
        """
        :return:  # A df with all of the samples and their intensities for all of the peaks
        # Index is peak ids
        """

        logger.debug('constructing sample/intensity df')

        logger.info("Generating a DF for a peak-compound and its intensities")
        samples = Sample.objects.all()
        peaks = Peak.objects.all()
        df_index = [p.id for p in peaks]

        # These two df are kept separately and concatenated at the end to preserve the datatype for the intensities
        columns = [s.name for s in samples]
        int_df = pd.DataFrame(index=df_index, columns=columns, dtype=float)

        # For each column (sample_name) get all of the peak intensites
        for c in columns:
            logger.debug("working on column %s" % c)
            peak_ints = SamplePeak.objects.filter(peak__id__in=df_index, sample__name=c).order_by(
                'peak_id').values_list('intensity', flat=True)
            int_df[c] = list(peak_ints)

        logger.info("There are %d peaks added to the intensity df" % int_df.shape[0])

        return int_df

    def  get_group_df(self, analysis, peaks):

        logger.info("Getting the peak group DF")
        start = timeit.default_timer()

        samples = SamplePeak.objects.filter(peak__in=peaks).order_by('peak_id').values_list('peak_id', 'intensity',
                                                                                            'sample_id__name',
                                                                                            'sample_id__group__name')
        columns = ['peak', 'intensity', 'filename', 'group']
        int_df = pd.DataFrame(samples, columns=columns)

        # gp_ids_all = ((AnalysisComparison.objects.filter(analysis=analysis).values_list('control_group', 'case_group')))
        # gp_ids = set(itertools.chain(*gp_ids_all))
        group_names = get_group_names(analysis)

        analysis_int_df = int_df[int_df['group'].isin(group_names)]

        group_series = analysis_int_df.groupby(["peak", "group"]).apply(self.get_average)
        # Put the returned series into a DF (KMCL: no idea why I can't keep the DF with the line above but this works)
        gp_df = group_series.to_frame()
        # Remove groups from the index and just keep peaks.
        group_df = gp_df.unstack()
        # Remove None from the column index and just keep the group
        group_df.columns = group_df.columns.get_level_values('group')

        stop = timeit.default_timer()
        logger.info("Generating the peak group dataframe took: %s " % str(stop - start))

        return group_df

    def get_average(self, group):
        """
        Takes in a df (in this case based on a group) and calculates the average intensity of the group.
        This is different from just a mean as we have to consider the NaN values properly.
        :return:
        """
        int_list = group.intensity.values
        if (np.isnan(int_list).all()):  # If all the values are NaN keep the value as NaN
            average_int = sum(int_list) / len(int_list)
        else:  # Take the average of the non-Nan numbers
            non_nan_length = (np.count_nonzero(~np.isnan(int_list)))
            average_int = np.nansum(int_list) / non_nan_length

        return average_int

    # This returns a DF with the groups/tissues and their average intensities and a maximum intensity for the row.
    def get_group_df_old(self, int_df):

        logger.info("Getting the sample groups with average intensitites (group_df)")

        samples = Sample.objects.all()
        sample_groups = set([sp.group.name for sp in samples])
        df_index = list(int_df.index.values)
        group_df = pd.DataFrame(index=df_index, columns=sample_groups, dtype=float)

        for group in sample_groups:
            logger.info("Working on group %s" % group)
            gp_samples = Sample.objects.filter(group__name=group)
            for i in df_index:
                int_list = []
                for g in gp_samples:
                    sample_name = g.name
                    intensity = int_df.loc[i, sample_name]
                    int_list.append(intensity)
                if (np.isnan(int_list).all()):  # If all the values are NaN keep the value as NaN
                    average_int = sum(int_list) / len(int_list)
                else:  # Take the average of the non-Nan numbers
                    non_nan_length = (np.count_nonzero(~np.isnan(int_list)))
                    average_int = np.nansum(int_list) / non_nan_length
                group_df.loc[i, group] = average_int
                # group_df.loc[i, group] = '%.2E' % Decimal(average_int)

        group_df['max_value'] = group_df.max(axis=1)

        group_sorted = group_df.reindex(sorted(group_df), axis=1)

        logger.info("Returning the group DF")
        return group_sorted

    def get_list_view_column_names(self, column_names, analysis):
        """
        A method to return user friendly column names given the group name. This also returns a heading for the maximum value
        This is created for the list view but could be modified for general use.
        :param column_names:This is the names of the groups.
        :return: Dictionary with group: user-friendly column name
        """
        group_name_dict, data_name_dict  = {}, {}
        groups = column_names

        samples = analysis.get_case_samples() | analysis.get_control_samples()

        group_fact_dict = self.get_group_tissue_ls_dicts(analysis, samples)

        for g in groups:
            if g == 'max_value':
                data_name_dict[g] = "Max" + " " + "Value"
            elif g == 'Metabolite':
                data_name_dict[g] = g
            elif g == 'cmpd_id':
                data_name_dict[g] = g
            elif g == 'm_z':
                data_name_dict[g] = "m/z"
            elif g == 'rt':
                data_name_dict[g] = "RT"
            elif g == 'id':
                data_name_dict[g] = "Peak ID"
            else:
                f_list = group_fact_dict[g]
                group_name_dict[g] = f_list[0]+" " + "(" + f_list[1] + ")"

        return group_name_dict, data_name_dict

    # KMcL: I think this is will only work with an intensity df of the high confidence DF.
    def get_single_cmpd_df(self, hc_int_df):
        """
        This method returns a dataframe of the grouped peaks (average values) without any duplicate compounds.
        It just takes the max value of the groups and keeps this if M+H and M-H it discards this.
        KMCL: We want to find the matching adduct and add give that the same preferred annotation.
        :return:
        """

        logger.info("Getting a DF of peaks containing with no duplicate compounds")

        group_df = self.get_group_df_old(hc_int_df)

        peak_sids = list(hc_int_df.index.values)
        compound_names = hc_int_df['Metabolite'].tolist()
        compound_ids = hc_int_df['cmpd_id'].tolist()
        group_df.insert(0, 'cmpd_id', compound_ids)
        group_df.insert(0, 'Metabolite', compound_names)

        duplicate_compounds = [item for item, count in collections.Counter(compound_names).items() if count > 1]
        sec_ids_to_delete = []

        for dc in duplicate_compounds:

            dup_peak_list = hc_int_df[hc_int_df.Metabolite == dc].index.values
            dup_peaks = Peak.objects.filter(id__in=dup_peak_list)
            max_values_dict = {}
            for dp in dup_peaks:
                max_value = group_df.loc[dp.id]['max_value']
                max_values_dict[dp.id] = max_value
            # logger.debug(max_values_dict)

            # Get the key with the maximum value to keep
            to_keep = max(max_values_dict.items(), key=operator.itemgetter(1))[0]
            keys = (list(max_values_dict.keys()))
            keys.remove(to_keep)
            # logger.debug("The smaller peaks are being deleted %s" % str(keys))
            for k in keys:
                sec_ids_to_delete.append(k)

        non_dup_ids = [sid for sid in peak_sids if sid not in sec_ids_to_delete]
        # Get a DF of cmpd_name, Group_columns and average values??
        non_dup_names_df = group_df.loc[non_dup_ids]

        logger.info("The number of (non-duplicate) compounds being returned is %s" % non_dup_names_df.shape[0])

        return non_dup_names_df

    def get_compound_details(self, peak_id, cmpd_id):
        """
        Method to return the compound parameters associated with a peak.
        :param peak_id: Id of the peak that you want the compound details for
        :return: A dictionary with compound details of the peak
        """

        ##KMCL: Current 1:1 for peak-compound so take the first - need to change to iterate through.

        peak = Peak.objects.get(id=peak_id)
        cmpd = Compound.objects.get(id=cmpd_id)
        annot = Annotation.objects.get(peak=peak, compound=cmpd)

        compound_details = {'inchikey': cmpd.inchikey, 'smiles': cmpd.smiles, 'cas_code': cmpd.cas_code,
                            'chebi_id': cmpd.chebi_id, 'related_chebi': cmpd.related_chebi,
                            'hmdb_id': cmpd.get_hmdb_id(), 'kegg_id': cmpd.get_kegg_id(), 'mz': peak.m_z,
                            'mass': annot.neutral_mass,
                            'rt': peak.rt, 'formula': cmpd.cmpd_formula, 'adduct': annot.adduct, 'name': cmpd.cmpd_name,
                            'identified': annot.identified, 'frank_annots': annot.frank_anno}

        return compound_details

    def get_simple_compound_details(self, cmpd_id):

        cmpd = Compound.objects.get(id=cmpd_id)

        cmpd_details = {'inchikey': cmpd.inchikey, 'smiles': cmpd.smiles, 'cas_code': cmpd.cas_code,
                        'chebi_id': cmpd.chebi_id, 'related_chebi': cmpd.related_chebi, 'hmdb_id': cmpd.get_hmdb_id(),
                        'kegg_id': cmpd.get_kegg_id(),
                        'formula': cmpd.cmpd_formula, 'name': cmpd.cmpd_name}

        return cmpd_details


    def get_groups(self, analysis, factor_name):

        """
        :param tissue: The tissue of interest
        :return: The groups that this tissue is found in
        """

        groups = Group.objects.filter(factor__name=factor_name)
        secondary_factor_type = get_factor_type_from_analysis(analysis, 'secondary_factor')
        samples = analysis.get_case_samples() | analysis.get_control_samples()

        sfactors = get_factors_from_samples(samples, secondary_factor_type)

        return groups, sfactors

    def get_gp_intensity(self, analysis, metabolite, factor_name, single_cmpds_df):

        """
        Given a metabolite and factor_name, this method returns the group name and the intensity.
        The average intensity has already been calculated in the single_cmpds_df
        This also returns the whole fly data for the compound for comparisons.

        :param metabolite:
        :param factor_name:
        :return: The group name of the factor and metabolite
        """

        groups, sfactors = self.get_groups(analysis, factor_name)  # This is the tissue groups without the whole fly
        analysis_comparisions = AnalysisComparison.objects.filter(analysis=analysis)

        all_groups = [ ]

        for g in groups:
            all_groups.append(g.name)
            all_groups.append(get_control_from_case(g.name,analysis_comparisions))

        met_search_df = single_cmpds_df[single_cmpds_df['Metabolite'] == metabolite]
        gp_int_dict = {}
        for g in all_groups:
            ave_intensity = met_search_df[g].values[0]
            gp_int_dict[g] = ave_intensity

        return gp_int_dict


    def get_group_tissue_ls_dicts(self, analysis, samples):
        # Given the name of the samples get dictionaries giving the groups: lifestage and/or tissue type of the group.

        primary_factor_type = get_factor_type_from_analysis(analysis, 'primary_factor')
        secondary_factor_type = get_factor_type_from_analysis(analysis, 'secondary_factor')

        gp_factor_dict = {}

        for s in samples:
            fact_dict = s.get_factor_dict()
            pfact = fact_dict[primary_factor_type]
            sfact = fact_dict[secondary_factor_type]
            gp_factor_dict[s.group.name] = [pfact, sfact]

        return gp_factor_dict

    def get_group_ints(self, metabolite, group, int_df):

        # Given a group and metabolite get back all of the intensities in that group as a list

        met_search_df = int_df[int_df['Metabolite'] == metabolite]
        peak_id = met_search_df.index

        met_int_df = int_df.loc[peak_id]

        sample_group = Sample.objects.filter(group__name=group)
        sample_names = [s.name for s in sample_group]

        sample_ints = met_int_df[sample_names].values[0]

        return list(sample_ints)

    def get_peak_id(self, metabolite, single_cmpd_df):

        # Given a metabolite name get the peak ID from the single_cmpds_df

        met_search_df = single_cmpd_df[single_cmpd_df['Metabolite'] == metabolite]
        peak_id = met_search_df.index.values[0]

        return peak_id

    def add_preferred_annotations(self, single_cmpds_df):
        """
        Takes in  the single_cmpds_df which is the single high confidence peak:compound df.
        :return: Adds the high confidence annotations as preferred to the peaks in this single-peak:single-cmpd df.
        """
        logger.debug("adding auto-generated preferred annotations")
        peaks_ids = single_cmpds_df.index.values
        cmpd_ids = single_cmpds_df.cmpd_id.values

        for pid, cid in zip(peaks_ids, cmpd_ids):
            peak = Peak.objects.get(id=pid)
            annot = Annotation.objects.get(peak=peak, compound__id=cid)
            peak.preferred_annotation = annot
            peak.preferred_annotation_reason = "Auto generated, high confidence annotation"
            peak.save()

            if annot.identified == 'True':
                annot.confidence = self.AUTO_I  # Annotation confidence level
            elif annot.frank_anno is not None:
                annot.confidence = self.AUTO_F

            annot.save()
        logger.debug("Auto generated, preferred annotations added")

    def update_std_cmpds(self):

        """
        This method is to check the compound database and for standard
        compounds that don't have any other associated  DB identifiers )that would make them useful for other methods).
        It updates the DB accordingly.
        """
        logger.info("Checking for Standard compounds without DB identifiers")

        KEGG = 2  # DB identifier for kegg - currenly the only search attempted for a  missing entry - this may need to be changed.

        cmpds = Compound.objects.all()
        # This was changed such that a std cmpd without other identifiers would be assigned the CompoundDBdetails
        # from another compound that matched in name. The name matching compound is then deleted.
        # Old code - git March 23 2020
        for c in cmpds:
            all_ids = c.get_all_identifiers()
            if len(all_ids) == 1 and 'stds_db' in all_ids:  # If the cmpd has a std Id and no other DB identifiers

                # If the compound name is found under a different compound ID add the std_db ID to this compound
                name_match = CompoundDBDetails.objects.filter(~Q(compound_id=c.id), cmpd_name=c.cmpd_name)
                if name_match:

                    matching_cmpd_id = name_match[0].compound_id  # Take the first/only matching compound.
                    matching_cmpd = Compound.objects.get(id=matching_cmpd_id)
                    logger.debug("We have a name match for the cmpd %s, which is  %s" % (c, matching_cmpd))

                    cmpd_detail_matches = CompoundDBDetails.objects.filter(compound_id=matching_cmpd_id)

                    for match_cmpd in cmpd_detail_matches:
                        match_cmpd.compound = c  # change the compound in the CompoundDBDetails to the std cmpd with no identifiers
                        match_cmpd.save()

                    matching_cmpd.delete()  # Delete matching cmpd as all of the

                else:  # no name match
                    # Currenly we only have kegg IDs in the dictonary - this will need refactored if this changes.
                    logger.debug("We have no name match for the cmpd %s" % c)

                    kegg_id = get_kegg_id(c.cmpd_name)
                    if kegg_id: #If the kegg_id is not none
                        db_name = DBNames.objects.get(id=KEGG)
                        new_cmpd_details, created_cmpd_details = CompoundDBDetails.objects.get_or_create(
                                db_name=db_name,
                                identifier=kegg_id,
                                cmpd_name=c.cmpd_name,
                                compound=c)

                        logger.debug("New cmpd details were created %s" % new_cmpd_details)
                        new_cmpd_details.save()
                    else:
                        #If this warning happens often we may want to look for HMDB or lipid map matches.
                        logger.warning("No KEGG ID could be found for %s. Consequently, ths std_cmpd "
                                       "has no associated DB ID" % c.cmpd_name)


def get_kegg_id(cmpd_name):
    """
    :param cmpd_name: The name of the compound for which we want to get the kegg_id
    :return: The kegg_id associated with the compound name or None if an association doesn't exist
    """

    logger.info ('finding a ID for %s' % cmpd_name)

    try:
        res = k.find('compound', cmpd_name)
        res = res.strip()
    except AttributeError as e:
        logger.info("Error %s looking for kegg_id " % e)
        res = None

    if res:
        tokens = res.split('\t')
        front = tokens[0].split(':')
        kegg_id = front[1]
    else:
        kegg_id = None

    return kegg_id
