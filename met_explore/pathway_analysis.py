import json
import traceback
from datetime import timedelta
from urllib.parse import quote

import numpy as np
import pandas as pd
import requests
from django.core.cache import cache
from django.utils import timezone
from loguru import logger
from pals.PLAGE import PLAGE
from pals.common import DATABASE_REACTOME_CHEBI, REACTOME_SPECIES_DROSOPHILA_MELANOGASTER
from pals.feature_extraction import DataSource
from scipy.sparse import coo_matrix
from django.core.exceptions import ObjectDoesNotExist
from tqdm import tqdm

from met_explore.compound_selection import CompoundSelector
from met_explore.helpers import load_object, save_object, get_control_from_case
from met_explore.models import SamplePeak, Sample, Annotation, DBNames, Compound, UniqueToken, Group, \
    AnalysisComparison, Analysis

CHEBI_BFS_RELATION_DICT ="chebi_bfs_relation_dict"
MIN_HITS = 2
PALS_FILENAME ='pals_df'
# """
# FixMe: For FlyMet the Analyses IDs for PALS are 1 and 3 this will be different for other projects
# this should be refactored.
# """
#
# ANALYSIS_IDS = [1,3]

def get_pals_ds(analysis):


    fly_int_df = get_pals_int_df(analysis)
    fly_exp_design = get_pals_experimental_design(analysis)
    chebi_df = get_single_db_entity_df('chebi_id')

    ds = DataSource(fly_int_df, chebi_df, fly_exp_design, DATABASE_REACTOME_CHEBI,
                    reactome_species=REACTOME_SPECIES_DROSOPHILA_MELANOGASTER)
    return ds


def get_cache_ds(analysis):
    # cache.delete('pals_ds')
    a_id = str(analysis.id)
    cache_name = 'pals_ds'+a_id

    if cache.get(cache_name) is None:
        logger.info("we dont have cache so running the pals_ds function")
        cache.set(cache_name, get_pals_ds(analysis), None)
        pals_ds = cache.get(cache_name)
    else:
        logger.info("we have cache for the pals ds, so retrieving it")
        pals_ds = cache.get(cache_name)

    return pals_ds


def get_pals_df(min_hits, analysis):
    ds = get_cache_ds(analysis)
    pals = PLAGE(ds, num_resamples=5000, seed=123)
    pathway_df_chebi = pals.get_pathway_df()
    pathway_df_return = pathway_df_chebi[pathway_df_chebi.tot_ds_F >= min_hits]

    return pathway_df_return

def get_cache_df(min_hits, analysis):

    fname = PALS_FILENAME+'_'+str(analysis.id)+".pkl"
    try:
        pals_df = pd.read_pickle("./data/" + fname)
        logger.info("The file %s has been found" % fname)

    except FileNotFoundError:

        logger.info("The file %s has not been found" % fname)
        pals_df = get_pals_df(min_hits, analysis)
        try:
            pals_df.to_pickle("./data/" + fname)
            logger.info("Written %s" % "./data/" + fname)

        except Exception as e:
            logger.error("Pickle didn't work because of %s ", e)
            traceback.print_exc()
            pass

    return pals_df


def get_cache_annot_df():
    # cache.delete('pals_annot_df')
    if cache.get('pals_annot_df') is None:
        logger.info("we dont have cache so running the pals_annot_df function")
        cache.set('pals_annot_df', get_pals_annot_df(), None)
        pals_annot_df = cache.get('pals_annot_df')
    else:
        logger.info("we have cache for the pals_annot_df, so retrieving it")
        pals_annot_df = cache.get('pals_annot_df')

    return pals_annot_df



def get_chebi_relation_dict():
    """
    A method to parse the chebi relation tsv and store the relationship we want in a dictionary
    :return: Dict with structure Chebi_id: [related_chebi_ids]
    """

    try:
        chebi_bfs_relation_dict = load_object("./data/" + CHEBI_BFS_RELATION_DICT + ".pkl")


    except Exception as e:

        logger.info("Constructing %s.pkl " % CHEBI_BFS_RELATION_DICT)

        try:
            chebi_relation_df = pd.read_csv("data/relation.tsv", delimiter="\t")

        except FileNotFoundError as e:

            logger.error("data/relation.tsv must be present")
            raise e

            # List of relationship we want in the dictionary
        select_list = ["is_conjugate_base_of", "is_conjugate_acid_of", "is_tautomer_of"]
        chebi_select_df = chebi_relation_df[chebi_relation_df.TYPE.isin(select_list)]

        chebi_relation_dict = {}
        # Gather all the INIT_IDs into a dictionary so that each INIT_ID is unique
        for ix, row in chebi_select_df.iterrows():
            init_id = str(row.INIT_ID)
            final_id = str(row.FINAL_ID)
            if init_id in chebi_relation_dict.keys():
                # Append the final_id onto the existing values
                id_1 = chebi_relation_dict[init_id]
                joined_string = ", ".join([id_1, final_id])
                chebi_relation_dict[init_id] = joined_string
            else:  # make a new key entry for the dict
                chebi_relation_dict[init_id] = final_id

        # Change string values to a list.
        graph = {k: v.replace(" ", "").split(",") for k, v in chebi_relation_dict.items()}

        chebi_bfs_relation_dict = {}
        for k, v in graph.items():
            r_chebis = bfs_get_related(graph, k)
            r_chebis.remove(k) #remove original key from list

            chebi_bfs_relation_dict[k] = r_chebis
        try:
            logger.info("saving chebi_relation_dict")
            save_object(chebi_bfs_relation_dict, "./data/" + CHEBI_BFS_RELATION_DICT + ".pkl")


        except Exception as e:
            logger.error("Pickle didn't work because of %s " % e)
            traceback.print_exc()
            pass


    return chebi_bfs_relation_dict


def get_related_chebi_ids(chebi_ids):
    """
    :param chebi_ids: A list of chebi IDS
    :return: A set of related chebi_IDs that are not already in the list
    """
    chebi_relation_dict = get_chebi_relation_dict()
    related_chebis = set()

    for c_id in chebi_ids:
        if c_id in chebi_relation_dict:
            related_chebis.update(chebi_relation_dict[c_id])

    return related_chebis


def bfs_get_related(graph_dict, node):
    """
    :param graph: Dictionary of key: ['value'] pairs
    :param node: the key for which all related values should be returned
    :return: All related keys as a list
    """
    visited = [] # List to keep track of visited nodes.
    queue = []     #Initialize a queue
    related_keys = []

    visited.append(node)
    queue.append(node)

    while queue:
        k = queue.pop(0)
        related_keys.append(k)

        for neighbour in graph_dict[k]:
          if neighbour not in visited:
            visited.append(neighbour)
            queue.append(neighbour)

    return related_keys


def get_pathway_id_names_dict():
    """
       Given a pathway ID get its name
       :return: pathway_id_names_dict
       """
    # Fixme: This is not analysis specfic (I think, KmcL) I believe any analysis should do
    #  A fix is for this is probably wise.

    analysis = Analysis.objects.get(name='Tissue Comparisons')

    pals_df = get_cache_df(MIN_HITS, analysis)
    pathway_id_names_dict = {}
    for ix, row in pals_df.iterrows():
        pathway_id_names_dict[row.pw_name] = ix

    return pathway_id_names_dict


def get_name_id_dict(analysis):
    """
    Given the name of a pathway get it's reactome ID
    :return: name_pw_id_dict
    """

    pals_df = get_cache_df(MIN_HITS, analysis)
    name_pw_id_dict = {}
    for ix, row in pals_df.iterrows():
        name_pw_id_dict[ix] = row.pw_name

    return name_pw_id_dict


def get_pals_int_df(analysis):
    """
    :return: A peak_id v sample_id DF containing all the peak intensity values.
    """
    logger.info("Getting the peak/sample intensity df")
    # Sample peaks are all the sample peaks that we want to look at - in the case of FlyMet this is all the peaks

    all_samples = analysis.get_case_samples() | analysis.get_control_samples()
    psi = SamplePeak.objects.filter(sample_id__in=all_samples).values_list('peak', 'sample', 'intensity')
    # psi = SamplePeak.objects.values_list('peak', 'sample', 'intensity')
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

    int_df = int_df.fillna(0)  # Change the NaN values to zero

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
    r_chebi_col ="related_chebi"
    db_names = DBNames.objects.all()
    columns = [d.db_name for d in db_names if d.db_name != 'stds_db']

    columns.insert(0, r_chebi_col)
    columns.insert(0, chebi_col)

    annotation_df = pd.DataFrame(columns=columns)
    annotation_df.insert(0, 'cmpd_ids', cmpd_ids)
    annotation_df.insert(0, 'peak_ids', peak_ids)

    for ix, row in tqdm(annotation_df.iterrows()):
        cmpd = Compound.objects.get(id=row.cmpd_ids)
        chebi_id = cmpd.chebi_id
        related_chebi = cmpd.related_chebi
        annotation_df.loc[ix, 'chebi_id'] = chebi_id
        annotation_df.loc[ix, 'related_chebi'] = related_chebi

        db_set = cmpd.compounddbdetails_set.all()
        for db in db_set:
            db_name = db.db_name.db_name
            if db_name != 'stds_db':
                # Get the DB reference and add it to the dataframe
                db_id = db.identifier
                annotation_df.loc[ix, db_name] = db_id

    logger.info("Returning the PALS annotation df")

    return annotation_df


def get_all_chebi_ids():

    fly_chebi_ids = set(Compound.objects.filter(chebi_id__isnull=False).values_list('chebi_id', flat=True))
    related_chebis = set(Compound.objects.filter(related_chebi__isnull=False).values_list('related_chebi', flat=True))

    # Split the string into indiviual chebi ids --> list of list
    split_related_chebis = [s.replace(" ", "").split(",") for s in related_chebis]
    # Change the above to a flat list
    fly_related_chebis = {chebi for sublist in split_related_chebis for chebi in sublist}

    all_chebi_ids = fly_chebi_ids.union(fly_related_chebis)

    return all_chebi_ids



def get_fly_pw_cmpd_formula(pw_id):
    """
    Method to return a cmpd_id: cmpd formula dictionary for a given pathway
    :param pw_id: The ID of the pathway for which the compound/formula dict is required
    :return: Dict with cmpd chebi_id: formula for each of the cmpds in a given pathway for the fly data
    """
    # Fixme: This is not analysis specfic. KmcL: I believe any analysis should do.
    #  A fix is probably wise.

    analysis = Analysis.objects.get(name='Tissue Comparisons')


    fly_pw_cmpd_for_dict = {}
    pals_df = get_cache_df(MIN_HITS, analysis)  # possibly member variables
    pals_ds = get_cache_ds(analysis)  # possibly member variables
    pathway_ids = pals_df.index.values

    # Grab all chebi_ids from the Fly DB
    # fly_chebi_ids = set(Compound.objects.filter(chebi_id__isnull=False).values_list('chebi_id', flat=True))
    fly_chebi_ids = get_all_chebi_ids()
    # For all of the pathways in reactome get the uniue cmpd_ids
    reactome_pw_unique_cmpd_ids = pals_ds.get_pathway_unique_cmpd_ids(pathway_ids)  # Possibly an member variable

    reactome_pw_cmpds = reactome_pw_unique_cmpd_ids[pw_id]
    fly_pw_cmpds = reactome_pw_cmpds.intersection(fly_chebi_ids)

    for cmpd in fly_pw_cmpds:
        formula = get_formula_set([cmpd])  # if only one element we still have to send as a list
        fly_pw_cmpd_for_dict[cmpd] = formula

    return fly_pw_cmpd_for_dict


def get_reactome_pw_metabolites(pw_id):
    """

    :param pw_id: The ID of the pathway
    :return: A list of metabolites associated with this Reactome pathway.
    """
    #Fixme: This is not analysis specfic. KmcL: I believe any analysis should do.
    # A fix is probably wise.

    analysis = Analysis.objects.get(name='Tissue Comparisons')

    pals_df = get_cache_df(MIN_HITS, analysis)  # possibly member variables
    pals_ds = get_cache_ds(analysis)  # possibly member variables
    pathway_ids = pals_df.index.values

    # Pass the summary table for the pathway from another function.
    # pwy_summ_table = pals_df.index

    reactome_pw_unique_cmpd_ids = pals_ds.get_pathway_unique_cmpd_ids(pathway_ids)  # Possibly an member variable
    reactome_pw_cmpds = reactome_pw_unique_cmpd_ids[pw_id]

    logger.debug("CMPDS %s" % reactome_pw_cmpds)

    return reactome_pw_cmpds


def get_formula_set(cmpd_list):
    """
    :param cmpd_list: List of compounds (chebi_ids)
    :return: list of unique formulas for those compounds
    """
    all_cmpds = Compound.objects.all()

    formula_list = set()
    for cmpd_id in cmpd_list:
        try:
            cmpd_formula = all_cmpds.get(chebi_id=cmpd_id).cmpd_formula
        except ObjectDoesNotExist:
            cmpd_formula = all_cmpds.get(related_chebi__contains = cmpd_id).cmpd_formula
        except Exception as e:
            raise e
        formula_list.add(cmpd_formula)

    return formula_list


def get_pals_single_entity_annot_df():
    ## This chooses one entity per compound to use for mapping to the patwhays - the order is: chebi, kegg, hmdb and then lipidmaps.
    """
    :param annot_cmpd_df: A dataframe with the peaks with all the available annotations for the compounds
    :return: Peak:entity ID DF - choses one DB ID for each peak compound
    """
    logger.info("Getting the single entity annotation df")
    annot_cmpd_df = get_cache_annot_df()

    no_identifiers = []
    annot_cmpd_df["entity_id"] = np.nan  # This will be the single, chosen identifier for the compound
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
        logger.error("There is a compound without a DB identifier %s" % msg)
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

    annot_cmpd_df = get_cache_annot_df()
    logger.info("Getting the annotation_df for %s" % id_type)
    annot_cmpd_df["entity_id"] = np.nan  # This will be the single, chosen identifier for the compound

    for ix, row in annot_cmpd_df.iterrows():
        if row[id_type] is not None:
            annot_cmpd_df.loc[ix, 'entity_id'] = row[id_type]
            if id_type == 'chebi_id' and row.related_chebi is not None:
                chebi_list = row.related_chebi.split(', ')
                for c in chebi_list:
                    new_row = annot_cmpd_df.loc[ix].copy()  # copy of the current row
                    new_row.entity_id = c #Add the related chebi to the entity list
                    add_row = pd.DataFrame([new_row])
                    annot_cmpd_df = pd.concat([annot_cmpd_df, add_row],ignore_index=True)


    annotation_df = annot_cmpd_df[['entity_id', 'peak_ids']]
    annotation_df.set_index('peak_ids', inplace=True)
    annotation_df.index.name = 'row_id'

    annot_df = annotation_df[annotation_df['entity_id'].notnull()].copy()

    return annot_df


def get_pals_experimental_design(analysis):

    cmpd_selector = CompoundSelector()

    analysis_comparisions = AnalysisComparison.objects.filter(analysis=analysis)

    controls = list(set([a.control_group.name for a in analysis_comparisions]))
    cases = list(set([a.case_group.name for a in analysis_comparisions]))

    groups =controls+cases

    # This gives a dictionary of orginal names: user readable names.
    group_dict, _ = cmpd_selector.get_list_view_column_names(groups, analysis)
    control_dict, _ = cmpd_selector.get_list_view_column_names(controls, analysis)
    case_dict, _ = cmpd_selector.get_list_view_column_names(cases, analysis)

    # User friendly names for use on the web
    control_names = [v for k, v in control_dict.items()]
    case_names = [v for k, v in case_dict.items()]

    exp_groups = {}  # Experimental group dictionary for use in the pals exp_design dict.
    for g in groups:
        samples = Sample.objects.filter(group__name=g)
        gp_files = [sample.name for sample in samples]
        exp_groups[group_dict[g]] = gp_files

    comparison_dict_list = []
    for c, case in zip(case_names, cases):
        comparison_dict = {}
        control = control_dict[get_control_from_case(case, analysis_comparisions)]
        comparison_dict['case'] = c
        comparison_dict['control'] = control
        comparison_dict['name'] = c + '/' + control

        comparison_dict_list.append(comparison_dict)

    experiment_design = {}
    experiment_design['groups'] = exp_groups
    experiment_design['comparisons'] = comparison_dict_list

    return experiment_design


def get_highlight_token():
    """
    A method to create or get the token for highlighting Reactome pathways using their Chebi IDS.
    This method would be easily adapted for other tokens.
    :return: The highlight token from the DB for use in Reactome pathways
    """

    time_now = timezone.now()
    highlight_token, token_created = UniqueToken.objects.get_or_create(name="reactome_highlight")

    if token_created:  # Add a description and save.
        highlight_token.description = "A token to highlight cmpds on a Reactome pathway based on their Chebi IDs"
        highlight_token.token = get_reactome_highlight_token()
        logger.info("A new token was created %s" % highlight_token)
        highlight_token.save()
    else:
        if highlight_token.datetime < (time_now - timedelta(days=7)):  # if the token has expired.

            logger.info("Reactome highlight token_expired requesting a new one")
            token = get_reactome_highlight_token()
            if token:  # If reactome returns a token update it, otherwsie do nothing and try next time.
                logger.info("updating token retrieval time so we know when it expires")
                highlight_token.token = token
                highlight_token.datetime = time_now
                highlight_token.save()
            else:
                logger.info("Reactome returned nothing so skipping token update for now")
        else:
            logger.info("Reactome token valid so no request for a new one required")
    logger.info("returning %s" % highlight_token.token)
    return highlight_token.token


def get_reactome_highlight_token():
    """
    Get the a token from Reactome that will highlight the metabolites present by their
    Chebi_IDs
    :return: token from the Reactome server that expires every 7 or so days or None if we don't get anything back from the server.
    """

    SPECIES = 'Drosophila melanogaster'

    cmpd_list = list(Compound.objects.values_list('chebi_id', flat=True).distinct())
    chebi_ids = [x for x in cmpd_list if x is not None]

    related_chebis = get_related_chebi_ids(chebi_ids)
    related_chebis.update(chebi_ids)

    unq_chebi_ids = list(related_chebis)

    logger.info("we have %s unq_chebi_ids" % len(unq_chebi_ids))

    data = '\t'.join(unq_chebi_ids)
    encoded_species = quote(SPECIES)

    url = 'https://reactome.org/AnalysisService/identifiers/?interactors=false&species=' + encoded_species + '&pageSize=20&page=1&sortBy=ENTITIES_PVALUE&order=ASC&resource=TOTAL&pValue=1&includeDisease=true'
    response = requests.post(url, headers={'Content-Type': 'text/plain'}, data=data.encode('utf-8'))

    status_code = response.status_code

    logger.debug("The response status code from Reactome %d" % status_code)

    if status_code == 200:
        json_response = json.loads(response.text)
        token = json_response['summary']['token']
    else:
        logger.warning("The response status code from Reactome suggests it failed %d" % status_code)
        token = None
    logger.info("Returning the Reactome token %s " % token)

    return token


def get_cmpd_pwys(cmpd_id):
    """
    Given a compound ID, return all of the pathways that compound is found in

    :param cmpd_id: The cmpd_id
    :return: List of pathways containing the compound.
    """
    #Fixme: I don't think it matters which analysis we use for this as the number of metabolites are for the
    # whole project. Might be worth a discussion/fix

    analysis = Analysis.objects.get(name='Tissue Comparisons')

    pals_ds = get_cache_ds(analysis)
    cmpd = Compound.objects.get(id=cmpd_id)
    cmpd_pw_dict = pals_ds.mapping_dict
    pwy_list = []

    try:
        if cmpd.chebi_id is not None:
            pwy_list = cmpd_pw_dict[cmpd.chebi_id]
    except KeyError:
        if cmpd.related_chebi is not None:
            alt_list = [chebi.strip() for chebi in cmpd.related_chebi.split(",")]
            for alt_c in alt_list:
                try:
                    pwy_list = cmpd_pw_dict[alt_c]
                    if pwy_list: #If we get a match return what we find a
                        break
                except KeyError:
                    logger.info ("No pathways returned for cmpd %s " % cmpd)
    return pwy_list