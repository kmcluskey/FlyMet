import os


def delete_if_exist(file_dir, file_path):
    full_path = os.path.abspath(os.path.join(file_dir, file_path))
    if os.path.exists(full_path):
        os.remove(full_path)
        print('Deleted %s' % full_path)


delete_if_exist('data', 'chebi_peak_df_cmpd_match_current.pkl')
delete_if_exist('data', 'chebi_peak_df_current.pkl')
delete_if_exist('data', 'chebi_unique_cmpd_ids_current.pkl')
delete_if_exist('data', 'current_chebi_peak_df.pkl')
delete_if_exist('data', 'current_hc_int_df.pkl')
delete_if_exist('data', 'current_prepared_df.pkl')
delete_if_exist('data', 'dup_removed_peak_df.pkl')
delete_if_exist('data', 'high_conf_peak_df.pkl')
delete_if_exist('data', 'peak_prepared_df.pkl')
