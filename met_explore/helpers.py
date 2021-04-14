import collections
import gzip
import itertools
import logging
import os
import pathlib
import pickle
import re
import sys
from collections import Counter

from loguru import logger

from met_explore.constants import LABEL_SEARCH_SECTIONS, LABEL_FACTOR_ORDER_DICT, LABEL_PROJECT_CONFIG, LABEL_ANALYSIS
from met_explore.models import Factor, Group, Analysis, AnalysisComparison, Sample


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def get_filename_from_string(fname):
    """
    A wee method to return a filename from a string without the extension.
    :param fname: a string containing a filename
    :return: file_name: a string containing the filename with no extension
    """
    f = open(fname)
    base_name = os.path.basename(f.name)
    os.path.splitext(base_name)
    file_name = os.path.splitext(base_name)[0]

    return file_name


def create_if_not_exist(out_dir):
    if not os.path.exists(out_dir) and len(out_dir) > 0:
        logger.info('Created %s' % out_dir)
        pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)


def save_object(obj, filename):
    """
    Save object to file
    :param obj: the object to save
    :param filename: the output file
    :return: None
    """
    out_dir = os.path.dirname(filename)
    create_if_not_exist(out_dir)
    logger.info('Saving %s to %s' % (type(obj), filename))
    with gzip.GzipFile(filename, 'w') as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_object(filename):
    """
    Load saved object from file
    :param filename: The file to load
    :return: the loaded object
    """
    with gzip.GzipFile(filename, 'rb') as f:
        return pickle.load(f)


def set_log_level_warning():
    logger.remove()
    logger.add(sys.stderr, level=logging.WARNING)


def set_log_level_info():
    logger.remove()
    logger.add(sys.stderr, level=logging.INFO)


def set_log_level_debug():
    logger.remove()
    logger.add(sys.stderr, level=logging.DEBUG)


def get_samples_by_factor(type, name):
    factors = Factor.objects.filter(type=type, name=name)
    groups = [f.group for f in factors]
    samples = Sample.objects.filter(group__in=groups)
    return samples


def get_samples_by_factors(types, names):
    assert len(types) == len(names)
    sets = []
    for i in range(len(types)):
        samples = set(get_samples_by_factor(types[i], names[i]))  # convert the list of samples to a set
        sets.append(samples)

    # https://stackoverflow.com/questions/2541752/best-way-to-find-the-intersection-of-multiple-sets
    intersection_results = set.intersection(*sets)
    return list(intersection_results)


# def get_factor_of_sample(sample, name):
#     results = Factor.objects.filter(sample=sample, name=name)
#     return results.first

def get_control_from_case(case, analysis_comparisions):
    """
    :param case: The group name of the sample that are the case in the study
    :return: String of the control group name
    """
    group = Group.objects.get(name=case)
    control = analysis_comparisions.get(case_group=group).control_group.name

    return control


def get_group_names(analysis):
    """
    A method to get all of the names of the groups given an analysis
    :param analysis:
    :return: list of group names (string)
    """

    gp_ids_all = ((AnalysisComparison.objects.filter(analysis=analysis).values_list('control_group', 'case_group')))
    gp_ids = set(itertools.chain(*gp_ids_all))
    group_names = [Group.objects.get(id=g).name for g in gp_ids]

    return group_names


def get_factor_type_from_analysis(analysis, factor_rank):
    """
    A method to return the primary factor or secondary factor given an analysis. Based on the number of instances of the factor type.
    :param analysis, factor_rank is either 'primary_factor' or 'secondary_factor'
    :return:
    """

    analysis_case_factors = Factor.objects.filter(group__case_group__analysis=analysis)
    factor_types = [a.type for a in analysis_case_factors if a.name != 'nan']

    try:
        config = get_project_config(analysis)
        factor_order_dict = config[LABEL_FACTOR_ORDER_DICT]
        ps_factors = [f for f in factor_types if f in factor_order_dict[factor_rank]]
        factor_count = Counter(ps_factors)
        ps_factor = max(factor_count, key=factor_count.get)
    except TypeError:
        ps_factor = None
    except ValueError:
        ps_factor = None
    return ps_factor


def get_factors_from_samples(samples, factor_type):
    """
    :param samples: queryset of samples to be used
    :param factor: Type of factor that we want the names for (string)
    :return: List of factor names (string)
    """
    factor_set = set()
    for s in samples:
        fact_dict = s.get_factor_dict()
        try:
            factor_set.add(fact_dict[factor_type])
        except KeyError as e:
            logger.info("This key is not of the factor type requested %s " % e)
            continue

    factor_list = list(factor_set)

    return factor_list


def get_project_config(analysis):
    config = analysis.category.project.metadata[LABEL_PROJECT_CONFIG]
    return config


UIConfig = collections.namedtuple('UIConfig', 'analysis category colnames case_label control_label')


def get_analysis_config(project_config, current_analysis_id):
    search_config = project_config[LABEL_SEARCH_SECTIONS]

    # search for the right config given the analysis name
    uic = None
    for config in search_config:
        analysis_name = config['analysis']
        ann = Analysis.objects.get(name=analysis_name)
        cat = ann.category
        if ann.id == current_analysis_id:
            current_category = cat.name
            colnames = config['colnames']
            case_label = config['case_label']
            control_label = config['control_label']
            uic = UIConfig(analysis=ann, category=current_category, colnames=colnames, case_label=case_label,
                           control_label=control_label)
    return uic


def get_search_categories(project_config):
    search_config = project_config[LABEL_SEARCH_SECTIONS]
    all_categories = []
    for config in search_config:
        analysis_name = config[LABEL_ANALYSIS]
        ann = Analysis.objects.get(name=analysis_name)
        cat = ann.category
        all_categories.append((cat.description, ann.id))
    return all_categories


def get_display_colnames(columns, colnames):
    display_colnames = []
    for col in columns:
        if col in colnames:
            display_colnames.append(colnames[col])
        else:
            display_colnames.append(col)
    return display_colnames
