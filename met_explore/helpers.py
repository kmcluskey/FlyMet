import os


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

