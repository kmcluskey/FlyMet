import gzip
import logging
import os
import pathlib
import pickle


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
        logging.info('Created %s' % out_dir)
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
    logging.info('Saving %s to %s' % (type(obj), filename))
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


