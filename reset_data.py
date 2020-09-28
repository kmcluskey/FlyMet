import os
import shutil
from pathlib import Path


def delete_file_if_exist(file_dir, file_path):
    full_path = os.path.abspath(os.path.join(file_dir, file_path))
    if os.path.exists(full_path):
        os.remove(full_path)
        print('Deleted %s' % full_path)


def delete_dir_if_exist(dir_name):
    dir_path = Path(dir_name).absolute()
    if dir_path.exists() and dir_path.is_dir():
        shutil.rmtree(dir_path)
        print('Deleted %s' % dir_path)


delete_file_if_exist('.', 'db.sqlite3')
delete_file_if_exist('data', 'chebi_peak_df_cmpd_match_current.pkl')
delete_file_if_exist('data', 'chebi_peak_df_current.pkl')
delete_file_if_exist('data', 'chebi_unique_cmpd_ids_current.pkl')
delete_file_if_exist('data', 'current_chebi_peak_df.pkl')
delete_file_if_exist('data', 'current_hc_int_df.pkl')
delete_file_if_exist('data', 'current_prepared_df.pkl')
delete_file_if_exist('data', 'dup_removed_peak_df.pkl')
delete_file_if_exist('data', 'high_conf_peak_df.pkl')
delete_file_if_exist('data', 'peak_prepared_df.pkl')
delete_dir_if_exist('django_cache')
