import gzip
import logging
import os
import pathlib
import pickle
import sys

from loguru import logger

from met_explore.models import Factor


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


def get_samples_by_factor(name, value):
    factors = Factor.objects.filter(name=name, value=value)
    samples = [factor.sample for factor in factors]
    return samples


def get_samples_by_factors(names, values):
    assert len(names) == len(values)
    sets = []
    for i in range(len(names)):
        samples = set(get_samples_by_factor(names[i], values[i])) # convert the list of samples to a set
        sets.append(samples)

    # https://stackoverflow.com/questions/2541752/best-way-to-find-the-intersection-of-multiple-sets
    intersection_results = set.intersection(*sets)
    return list(intersection_results)


def get_factor_of_sample(sample, name):
    results = Factor.objects.filter(sample=sample, name=name)
    return results.first()