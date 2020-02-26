import os
import numpy as np
import pandas as pd
import sys
import logging
sys.path.append('/Users/Karen/PALS/')

import pals
from pals.pimp_tools import get_pimp_API_token_from_env, PIMP_HOST, download_from_pimp, get_ms1_peaks
from pals.feature_extraction import DataSource
from pals.PALS import PALS
from pals.ORA import ORA
from pals.common import *
from scipy.sparse import coo_matrix
from django.core.cache import cache, caches


from met_explore.models import *
from met_explore.compound_selection import CompoundSelector

logger = logging.getLogger(__name__)

def get_pals_ds():

    fly_int_df = get_pals_int_df()
    fly_exp_design = get_pals_experimenal_design()
    chebi_df = get_single_db_entity_df('chebi_id')

    ds = DataSource(fly_int_df, chebi_df, fly_exp_design, DATABASE_REACTOME_CHEBI,reactome_species=REACTOME_SPECIES_DROSOPHILA_MELANOGASTER)
    return ds

def get_cache_ds():

    if cache.get('pals_ds') is None:
        logger.info("we dont have cache so running the function")
        cache.set('pals_ds', get_pals_ds(), 60 * 180000)
        pals_ds = cache.get('pals_ds')
    else:
        logger.info("we have cache for the pals ds, so retrieving it")
        pals_ds = cache.get('pals_ds')

    return pals_ds

def get_pals_df():

    ds = get_cache_ds()

    pals = PALS(ds, plage_weight=5, hg_weight=1)
    pathway_df_chebi = pals.get_pathway_df()

    print ("going to add formulas")
    pw_df_chebi = add_num_fly_formulas(ds, pathway_df_chebi)

    return pw_df_chebi



def get_pals_int_df():
    """
    :return: A peak_id v sample_id DF containing all the peak intensity values.
    """
    logger.info("Getting the peak/sample intensity df")
    # Sample peaks are all the sample peaks that we want to look at - in the case of FlyMet this is all the peaks
    psi = SamplePeak.objects.values_list('peak', 'sample', 'intensity')
    peaks, samples, intensities = zip(*psi)
    dpeaks = sorted(list(set(peaks)))
    dsamples = sorted(list(set(samples)))
    peakdict = dict(zip(dpeaks, range(len(dpeaks))))
    sampledict = dict(zip(dsamples, range(len(dsamples))))

    rows = [peakdict[_] for _ in peaks]
    cols = [sampledict[_] for _ in samples]
    data = coo_matrix((intensities, (rows, cols)), dtype=np.float32)
    sample_names = Sample.objects.filter(id__in=dsamples).order_by('id').values_list('name', flat=True)

    int_df = pd.DataFrame(data.todense(), index=dpeaks, columns=sample_names)
    int_df.replace(0, np.nan, inplace=True)
    int_df.index.name = "row_id"

    int_df = int_df.fillna(0) #Change the NaN values to zero

    logger.info("Returning the peak/sample intensity df")

    return int_df



def get_pals_annot_df():
    """
    This returns a DF of peaks where each row, of the same peak, is for a different compounds with columns
    containing all known identifiers.

    :return: A full annotation dataframe for all the annotated peaks in Fly
    """
    logger.info("Getting the full annotation df")
    annotation_data = Annotation.objects.values_list('peak', 'compound')
    peaks, compounds = zip(*annotation_data)

    peak_ids = list(peaks)
    cmpd_ids = list(compounds)

    chebi_col = 'chebi_id'
    db_names = DBNames.objects.all()
    columns = [d.db_name for d in db_names if d.db_name != 'stds_db']

    columns.insert(0, chebi_col)

    annotation_df = pd.DataFrame(columns=columns)
    annotation_df.insert(0, 'cmpd_ids', cmpd_ids)
    annotation_df.insert(0, 'peak_ids', peak_ids)

    for ix, row in annotation_df.iterrows():
        cmpd = Compound.objects.get(id=row.cmpd_ids)
        chebi_id = cmpd.chebi_id
        annotation_df.loc[ix, 'chebi_id'] = chebi_id

        db_set = cmpd.compounddbdetails_set.all()
        for db in db_set:
            db_name = db.db_name.db_name
            if db_name != 'stds_db':
                # Get the DB reference and add it to the dataframe
                db_id = db.identifier
                annotation_df.loc[ix, db_name] = db_id

    logger.info("Returning the PALS annotation df")

    return annotation_df


def add_num_fly_formulas(pals_ds, pals_df):
    """

    :param pals_ds: The pals datasource for this experiment
    :param pals_df: The original pals df
    :return: Pals DF with the unique formulas belonging to the annotated compound in a dataset
    """
    print ("adding  the formula stuff")
    logger.info("Adding Fly F to the pals DF")
    pathway_ids = pals_df.index.values

    fly_chebi_ids = set(Compound.objects.filter(chebi_id__isnull=False).values_list('chebi_id', flat=True))
    reactome_pw_unique_cmpd_ids = pals_ds.get_pathway_unique_cmpd_ids(pathway_ids)

    for index, row in pals_df.iterrows():
        reactome_pw_cmpds = reactome_pw_unique_cmpd_ids[index]
        fly_pw_cmpds = reactome_pw_cmpds.intersection(fly_chebi_ids)
        fly_pw_formula = get_formula_set(list(fly_pw_cmpds))

        pals_df.loc[index, 'tot_ds_F'] = len(fly_pw_formula)

    # pals_df_fly = pals_df.drop('tot_ds_F', axis=1).copy() #Drop the calculation of DF formula
    pals_df['tot_ds_F'] = pals_df['tot_ds_F'].astype(int) #Make sure this new column has int values

    # Recalculate the coverage for the new values.
    pals_df['F_coverage'] = (((pals_df['tot_ds_F']) / pals_df['unq_pw_F']) * 100).round(2)

    return pals_df


def get_formula_set(cmpd_list):
    """
    :param cmpd_list: List of compounds (chebi_ids)
    :return: list of unique formulas for those compounds
    """
    all_cmpds = Compound.objects.all()

    formula_list = set()
    for cmpd_id in cmpd_list:
        cmpd_formula = all_cmpds.get(chebi_id=cmpd_id).cmpd_formula
        formula_list.add(cmpd_formula)

    return formula_list






def get_pals_single_entity_annot_df():
    ## This chooses one entity per compound to use for mapping to the patwhays - the order is: chebi, kegg, hmdb and then lipidmaps.
    """
    :param annot_cmpd_df: A dataframe with the peaks with all the availbale annotations for the compounds
    :return: Peak:entity ID DF - choses one DB ID for each peak compound
    """
    logger.info("Getting the single entity annotation df")
    annot_cmpd_df = get_pals_annot_df()

    no_identifiers = []
    annot_cmpd_df["entity_id"] = np.nan # This will be the single, chosen identifier for the compound
    for ix, row in annot_cmpd_df.iterrows():
        if row.chebi_id is not None:
            annot_cmpd_df.loc[ix, 'entity_id'] = row.chebi_id
        elif (pd.notnull(row.kegg)):
            annot_cmpd_df.loc[ix, 'entity_id'] = row.kegg
        elif (pd.notnull(row.hmdb)):
            annot_cmpd_df.loc[ix, 'entity_id'] = row.hmdb
        elif (pd.notnull(row.lipidmaps)):
            annot_cmpd_df.loc[ix, 'entity_id'] = row.lipidmaps
        else:
            no_identifiers.append(row.cmpd_ids)

    # Check that all compound have an identifier - no identifiers should be an empty list
    try:
        num_cmpds_no_id = len(no_identifiers)
        assert (num_cmpds_no_id == 0), "All compounds should have an identifier"
    except AssertionError as msg:
        logger.error("There is a compound without a DB identfier %s", msg)
        raise

    annotation_df = annot_cmpd_df[['entity_id', 'peak_ids']]
    annotation_df.set_index('peak_ids', inplace=True)
    annotation_df.index.name = 'row_id'

    logger.info("Returning the single entity annotation df")

    return annotation_df


def get_single_db_entity_df(id_type):
    """

    :param annot_cmpd_df: A DF containing all of the various identifiers with id_type as columns
    :param id_type: The DB ID that has to be returned
    :return: A dataframe containing peaks and all the compounds from a particular DB
    """

    annot_cmpd_df = get_pals_annot_df()
    logger.info("Getting the annotation_df for %s", id_type)
    annot_cmpd_df["entity_id"] = np.nan  # This will be the single, chosen identifier for the compound

    for ix, row in annot_cmpd_df.iterrows():
        if row.chebi_id is not None:
            annot_cmpd_df.loc[ix, 'entity_id'] = row[id_type]

    annotation_df = annot_cmpd_df[['entity_id', 'peak_ids']]
    annotation_df.set_index('peak_ids', inplace=True)
    annotation_df.index.name = 'row_id'

    annot_df = annotation_df[annotation_df['entity_id'].notnull()].copy()

    return annot_df


def get_pals_experimenal_design():
    cmpd_selector = CompoundSelector()
    samples = Sample.objects.all()

    groups = list(set([s.group for s in samples]))  # Names of all the groups
    controls = ['Whole_f', 'Whole_m', 'Whole_l']  # The current control groups
    cases = [g for g in groups if g not in controls]  # Groups not in the control group

    # This gives a dictionary of orginal names: user readable names.
    group_dict = cmpd_selector.get_list_view_column_names(groups)
    control_dict = cmpd_selector.get_list_view_column_names(controls)
    case_dict = cmpd_selector.get_list_view_column_names(cases)

    # User friendly names for use on the web
    control_names = [v for k, v in control_dict.items()]
    case_names = [v for k, v in case_dict.items()]

    exp_groups = {}  # Experimental group dictionary for use in the pals exp_design dict.
    for g in groups:
        sample = Sample.objects.filter(group=g)
        gp_files = list(sample.values_list('name', flat=True))
        exp_groups[group_dict[g]] = gp_files

    comparison_dict_list = []
    for c in case_names:
        comparison_dict = {}
        control = get_control_from_case(c)
        comparison_dict['case'] = c
        comparison_dict['control'] = control
        comparison_dict['name'] = c + '/' + control

        comparison_dict_list.append(comparison_dict)

    experiment_design = {}
    experiment_design['groups'] = exp_groups
    experiment_design['comparisons'] = comparison_dict_list

    return experiment_design



def get_control_from_case(case):
    """

    :param case: The group name of the sample that are the casein the study
    :return:
    """

    if '(F)' in case:
        control = "Whole (F)"
    elif '(L)' in case:
        control = "Whole (L)"
    elif '(M)' in case:
        control = "Whole (M)"
    else:
        logger.error("There is no control to match the passed case, returning None")
        control = None

    return control





