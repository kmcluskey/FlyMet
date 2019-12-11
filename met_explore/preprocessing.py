import pandas as pd
import re
import numpy as np
import logging
# from met_explore.peak_selection import PeakSelector

logger = logging.getLogger(__name__)

# Names to pickle the files as we go along so changes can be made without running all of the methods again.
CHEBI_DF_NAME = "chebi_ontology_df_PERMANENT"
ADDED_CHEBI_NAME = "chebi_peak_df_current"
CHEBI_CMPD_MATCH = "chebi_peak_df_cmpd_match_current"
CHEBI_UNIQUE_IDS = "chebi_unique_cmpd_ids_current"
CMPDS_FINAL = "current_chebi_peak_df"


class PreprocessCompounds(object):
    """
    This is a class to preprocess the compounds and give them unique Chebi IDS and add references e.g. smiles etc from the chebi DB.
    """

    def __init__(self, peak_df):

        self.peak_df = peak_df
        self.chebi_df = self.construct_chebi_ontology_df()


    def get_preprocessed_cmpds(self):

        self.add_chebi_ids()
        self.give_each_chebi_same_id()
        self.give_chebi_inchi_unique_id()
        self.collect_dup_cmpds_no_chebi()
        self.change_std_cmpds_no_chebi()

        return self.peak_df

    # def get_preprocessed_cmpds(self):
    #
    #     self.preprocess_cmpds()
    #
    #     return self.peak_df

    def get_chebi_ontology_df(self):

        return self.chebi_df

    def add_chebi_ids(self):
        """
        Method to add Chebi IDS to our peak list DF for all of the compounds.
        :return:
        """
        logger.info("Adding the chebi_ids")

        try:
            self.peak_df = pd.read_pickle("./data/" + ADDED_CHEBI_NAME + ".pkl")  # KMCL - this file should be named after the input files so not to repeat.
            logger.info("The file %s has been found: ", ADDED_CHEBI_NAME)

        except FileNotFoundError:

            self.peak_df["chebi_id"] = None # Add empty column to fill in.
            self.peak_df["chebi_name"] = None

            for index, row in self.peak_df.iterrows():

                set_chebi_id = row.chebi_id
                identifier = row.identifier
                inchi = row.inchikey
                formula = row.formula

                if not set_chebi_id:
                    print("The identifier/inchi/formula are ", identifier, inchi, formula)

                    chebi_id, chebi_id_inchi = self.get_chebi_id(identifier, inchi, formula)

                    print ("ID and ID_INCHI", chebi_id, chebi_id_inchi)

                    # If both exist add the chebi_id (based on the DB identifier) to the DF
                    if chebi_id and chebi_id_inchi:
                        logger.info("The ID and chebi_id are both found: %s %s", chebi_id, chebi_id_inchi)
                        logger.info("Adding the chebi_id %s", chebi_id)
                        self.peak_df.loc[index, 'chebi_id'] = chebi_id

                        # Get the chebi inchi if it exists & If it's not null add it to the DF.
                        inchi = self.chebi_df[self.chebi_df.chebi_id == chebi_id].inchikey.values[0]
                        print ("The inchi that we found is ", inchi)
                        if not pd.isnull(inchi):
                            print ("in the wee setting bit")
                            self.peak_df.loc[index, 'inchikey'] = inchi

                    elif chebi_id and not chebi_id_inchi:
                        logger.info('chebi_id and not chebi_id_inchi, adding %s', chebi_id)
                        self.peak_df.loc[index, 'chebi_id'] = chebi_id

                        # Grab the inchi from the chebi_id if it exists.
                        inchi = self.chebi_df[self.chebi_df.chebi_id == chebi_id].inchikey.values[0]
                        if not pd.isnull(inchi):
                            self.peak_df.loc[index, 'inchikey'] = inchi

                    elif chebi_id_inchi and not chebi_id:
                        print('chebi_id_inchi and not chebi_id adding chebi_id_inchi ', chebi_id_inchi)
                        self.peak_df.loc[index, 'chebi_id'] = chebi_id_inchi
                        #As the chebi_id was obtained using the inchi we can leave that inchi as the original one.

                    elif not chebi_id_inchi and not chebi_id:
                        chebi_id = None
                        logger.info("No chebi ID found so setting it to None")
                        self.peak_df.loc[index, 'chebi_id'] = chebi_id

            ## Add Chebi names, smile and cas-codes to the peak DF
            for index, row in self.peak_df.iterrows():
                if row.chebi_id:  # If not a null value
                    chebi_id = row.chebi_id
                    chebi_name = self.chebi_df[self.chebi_df.chebi_id == chebi_id].chebi_name.values[
                        0]
                    smiles = self.chebi_df[self.chebi_df.chebi_id == chebi_id].smiles.values[
                        0]
                    cas_code = self.chebi_df[self.chebi_df.chebi_id == chebi_id].cas_code.values[
                        0]
                    print(chebi_id, chebi_name)
                    self.peak_df.loc[index, 'chebi_name'] = chebi_name
                    self.peak_df.loc[index, 'cas_code'] = cas_code
                    self.peak_df.loc[index, 'smiles'] = smiles


            try:
                self.peak_df.to_pickle("./data/"+ ADDED_CHEBI_NAME+".pkl")
            except Exception as e:
                logger.error("Pickle didn't work because of %s ", e)
                pass


    def give_each_chebi_same_id(self):
        """
        # Give all rows with the same chebi_id the same cmpd ID in the peak_df
        """
        logger.info("Making sure each Chebi_ID has the same cmpd_id")
        try:
            self.peak_df = pd.read_pickle(
                "./data/" + CHEBI_CMPD_MATCH + ".pkl")  # KMCL - this file should be named after the input files so not to repeat.
            logger.info("The file %s has been found: ", CHEBI_CMPD_MATCH)

        except FileNotFoundError:

            chebi_ids = self.peak_df.chebi_id.unique()

            for c_id in chebi_ids:

                single_chebi_df = self.peak_df[self.peak_df['chebi_id'] == c_id]
                indexes = single_chebi_df.index.values
                cmpd_ids = single_chebi_df.cmpd_id.unique()
                no_cmpd_ids = len(cmpd_ids)

                if no_cmpd_ids > 1:
                    cmpd_id = cmpd_ids[0]  # Take the first cmpd_id and rename all the rows with the same chebi Id
                    print("should be replacing all with this cmpd_id ", cmpd_id)
                    self.peak_df.loc[indexes, 'cmpd_id'] = cmpd_id

            try:
                self.peak_df.to_pickle("./data/" + CHEBI_CMPD_MATCH + ".pkl")
            except Exception as e:
                logger.error("Pickle didn't work because of %s ", e)
                pass


    def give_chebi_inchi_unique_id(self):
        """
        A Method that makes sure that each unique chebi ID, Inchi and formula given individual cmpd_ids (at this stage).
        If there are duplicate compounds with the same ID it gives a new ID to one of the chebi_ids, inchi_keys and/or formulas.
        :return:
        """
        logger.info("Checking if chebi, inchi and formulas all have unique cmpd_ids")
        try:
            self.peak_df = pd.read_pickle(
                "./data/" + CHEBI_UNIQUE_IDS + ".pkl")  # KMCL - this file should be named after the input files so not to repeat.
            logger.info("The file %s has been found: ", CHEBI_UNIQUE_IDS)

        except FileNotFoundError:
            max_cmpd_id = self.peak_df['cmpd_id'].max()

            cmpd_ids = self.peak_df.cmpd_id.unique()
            for cmpd in cmpd_ids:

                single_cmpd_df = self.peak_df[self.peak_df['cmpd_id'] == cmpd]

                inchi_keys = single_cmpd_df.inchikey.unique()
                # no_present_inchi = sum(1 for _ in filter(None.__ne__, inchi_keys))
                present_inchis = inchi_keys[inchi_keys != np.array(None)]
                no_inchi_keys = len(inchi_keys)

                chebi_ids = single_cmpd_df.chebi_id.unique()
                present_chebi_ids = chebi_ids[chebi_ids != np.array(None)]

                formulas = single_cmpd_df.formula.unique()
                no_formulas = len(formulas)

                neutral_masses = (single_cmpd_df.neutral_mass.round(2).unique())
                nm_diff = np.diff(neutral_masses)
                h_diff = np.isclose([nm_diff], [1.01], atol=0.03)  # Diff is mass is about a proton
                dbs = single_cmpd_df.db.unique()

                # Same compound IDs, different CheBi_ids - give the row a new cmpd_id = Max cmpd_id +1
                if len(present_chebi_ids) > 1:  # If the inchi keys are 1 and None just leave.

                    logger.info("This compound id %s has more than one chebi_id %s",cmpd, chebi_ids )

                    if len(present_chebi_ids) == len(chebi_ids):  # There are no missing/None chebi_ids

                        for c in present_chebi_ids[1:]:
                            max_cmpd_id += 1
                            # Take one of the chebi_ids and give it a new cmpd id
                            scmpd_id_df = single_cmpd_df[single_cmpd_df.chebi_id == c]
                            change_indexes = scmpd_id_df.index.values
                            self.peak_df.loc[change_indexes, 'cmpd_id'] = max_cmpd_id

                    elif len(present_chebi_ids) < len(chebi_ids):  # There are missing chebi ids values
                        for c in present_chebi_ids:  # Change the ID of the present inchi and leave those with None
                            max_cmpd_id += 1
                            # Take one of the inchikeys and give it a new id
                            scmpd_id_df = single_cmpd_df[single_cmpd_df.chebi_id == c]
                            change_indexes = scmpd_id_df.index.values
                            self.peak_df.loc[change_indexes, 'cmpd_id'] = max_cmpd_id

                # If one of these is a standard compound and the difference in the formula is an H change the adduct to M and
                # the formula to match the one of the non-standard cmpd.
                if (no_formulas > 1) and ('stds_db' in dbs) and h_diff:

                    stds_df = single_cmpd_df[single_cmpd_df.db == 'stds_db']
                    change_indexes = stds_df.index.values
                    neutral_mass = stds_df.mass.values[0]
                    print(change_indexes)

                    non_stds_df = single_cmpd_df[single_cmpd_df.db != 'stds_db']
                    formula = non_stds_df.formula.values[0]
                    chebi_id = non_stds_df.chebi_id.values[0]
                    chebi_name = non_stds_df.chebi_name.values[0]
                    adduct = 'M'

                    self.peak_df.loc[change_indexes, ['formula', 'chebi_id', 'chebi_name', 'adduct',
                                                        'neutral_mass']] = formula, chebi_id, chebi_name, adduct, neutral_mass

                # Same compound IDs but different formulas and no std compound - change the cmpd id.
                elif no_formulas > 1 :
                    logger.info("This compound id %s has more than one inchi_key %s",cmpd, formulas )
                    for f in formulas[1:]: #Keep the first formula, change the rest
                        max_cmpd_id +=1
                        scmpd_id_df = single_cmpd_df[single_cmpd_df.formula==f]
                        change_indexes = scmpd_id_df.index.values
                        self.peak_df.loc[change_indexes,'cmpd_id']= max_cmpd_id

                # Check for dulicate inchikeys
                # If the inchi keys are 1 and None just leave alone - more than one non null value and if one chebi_id leave as one cmpd
                if len(present_inchis) > 1 and len(chebi_ids) !=1:
                    logger.info("This compound id %s has more than one inchi_key %s",cmpd, inchi_keys )
                    if len(present_inchis) == no_inchi_keys:  # There are no missing/None values for inchikeys

                        for i in present_inchis[1:]:
                            max_cmpd_id += 1
                            # Take one of the inchikeys and give it a new id
                            scmpd_id_df = single_cmpd_df[single_cmpd_df.inchikey == i]
                            change_indexes = scmpd_id_df.index.values
                            self.peak_df.loc[change_indexes, 'cmpd_id'] = max_cmpd_id

                    elif len(present_inchis) < no_inchi_keys:  # There are missing values
                        for i in present_inchis:  # Change the ID of the present inchi and leave those with None
                            max_cmpd_id += 1
                            # Take one of the inchikeys and give it a new id

                            scmpd_id_df = single_cmpd_df[single_cmpd_df.inchikey == i]
                            change_indexes = scmpd_id_df.index.values
                            self.peak_df.loc[change_indexes, 'cmpd_id'] = max_cmpd_id

            try:
                self.peak_df.to_pickle("./data/" + CHEBI_UNIQUE_IDS + ".pkl")
            except Exception as e:
                logger.error("Pickle didn't work because of %s ", e)
                pass


    def collect_dup_cmpds_no_chebi(self):
        """
        Many compounds without chebi_ids are duplicated because they have no inchikeys - this method
        collects the compounds that have the same name and same db identifier into a single compound
        :return:
        """

        logger.info("Collecting compounds with same names/identifiers that have no chebi_id")

        try:
            self.peak_df = pd.read_pickle("./data/" + CMPDS_FINAL + ".pkl")  # KMCL - this file should be named after the input files so not to repeat.
            logger.info("The file %s has been found: ", CMPDS_FINAL)

        except FileNotFoundError:

            no_chebis = self.peak_df[self.peak_df['chebi_id'].isnull()]
            no_chebis_cmpd_names = no_chebis['compound'].unique()

            for cmpd in no_chebis_cmpd_names:

                single_name_df = no_chebis[no_chebis['compound'] == cmpd]
                inchi_keys = single_name_df.inchikey.unique()
                present_inchis = inchi_keys[inchi_keys != np.array(None)]
                db_identifiers = single_name_df.identifier.unique()

                cmpd_ids = single_name_df['cmpd_id'].unique()

                # If we have more than one compound id and this is not a result of two different inchikeys
                if (len(cmpd_ids) > 1) and (len(cmpd_ids) != len(present_inchis)):
                    for db_id in db_identifiers:
                        single_db_id_df = single_name_df[single_name_df['identifier'] == db_id]
                        indexes = single_db_id_df.index.values
                        single_id_cmpd_ids = single_db_id_df.cmpd_id.unique()
                        no_cmpd_ids = len(single_id_cmpd_ids)
                        # For each compound of the same identifier - make it a single cmpd.
                        if no_cmpd_ids > 1:
                            cmpd_id = cmpd_ids[0]  # Take the first cmpd_id and rename all the rows with the same chebi Id
                            print("should be replacing all with this cmpd_id ", cmpd_id)
                            self.peak_df.loc[indexes, 'cmpd_id'] = cmpd_id

            try:
                self.peak_df.to_pickle("./data/" + CMPDS_FINAL + ".pkl")
            except Exception as e:
                logger.error("Pickle didn't work because of %s ", e)
                pass

    def change_std_cmpds_no_chebi(self):
        """
        A method to collect any std_cmpds with no chebi and match them to other cmpds with the same Inchikeys
        :return:
        """
        stds_db = self.peak_df['db'] == 'stds_db'
        no_chebi = self.peak_df['chebi_id'].isnull()
        stds_no_chebi = self.peak_df[stds_db & no_chebi] #DF that contains standard compounds with no chebi_ids

        unique_inchis = stds_no_chebi.inchikey.unique()

        for inchi in unique_inchis:
            inchi_df = self.peak_df[self.peak_df['inchikey'] == inchi]
            cmpd_ids = list(inchi_df.cmpd_id.unique())
            num_cmpd_ids = len(cmpd_ids)
            # If there is more than one cmpd_id with this inchi
            if num_cmpd_ids > 1:
                # give them all the same cmpd_id?
                for c in cmpd_ids:
                    cmpd_id_df = self.peak_df[self.peak_df['cmpd_id'] == c]
                    no_chebi_id = cmpd_id_df['chebi_id'].isnull().unique()[0] #Check if this is the cmpd without the chebi_id
                    std_db = (cmpd_id_df.db == 'stds_db').values[0]

                    if (no_chebi_id and std_db): #If it's the standard cmpd with no chebi id
                        new_cmpd_id = [x for x in cmpd_ids if x != c] #Remove c (without the chebi_id from the list)
                        indexes_to_change = cmpd_id_df.index
                        self.peak_df.loc[indexes_to_change, 'cmpd_id'] = new_cmpd_id



    def get_chebi_id(self, identifier, inchikey, formula):
        """
        A method to return the chebi ID from a DB identifier and/or the listed inchikey
        :param identifier: The DB identifier
        :param inchikey: The compound inchikey
        :param formula: The compound formula
        :return: chebi_id, chebi_inchi_id - chebi_ids from the identifier and from the inchikey
        """

        chebi_inchi_id = None
        chebi_id = None

        # Get the chebi_id based on Inchi - hopefully when found it matches the one on ID.
        if inchikey is not None:

            logger.info("Trying to get Chebi on Inchi")
            try:
                chebi_match = self.chebi_df[self.chebi_df['inchikey'] == inchikey]
                if not chebi_match.empty:
                    chebi_inchi_id = self.get_formula_match(chebi_match, formula, None)

            except KeyError as e:
                logger.info("No match to chebi for this inchi %s ", inchikey)
                chebi_inchi_id = None
                # Return the value and not the array

        if chebi_inchi_id:
            chebi_inchi_id = chebi_inchi_id[0]



        if identifier.startswith('C'):  # Kegg identifier
            try:
                chebi_match = self.chebi_df[self.chebi_df['kegg_id'] == identifier]
                if not chebi_match.empty:
                    chebi_id = self.get_formula_match(chebi_match, formula, chebi_inchi_id )
                    print ("HERE2 ", chebi_id)

            except KeyError as e:
                logger.info("No match to chebi for this kegg id %s", identifier)
                chebi_id = None

        elif identifier.startswith('HMDB'):
            hmdb_no = self.get_hmdb_no(identifier)
            try:
                chebi_match = self.chebi_df[self.chebi_df['hmdb_id'] == hmdb_no]
                if not chebi_match.empty:
                    chebi_id = self.get_formula_match(chebi_match, formula, chebi_inchi_id)
            except KeyError as e:
                logger.info("No match to chebi for this hmdb id %s", identifier)
                chebi_id = None

        elif identifier.startswith('LM'):
            try:
                chebi_match = self.chebi_df[self.chebi_df['lmaps_id'] == identifier]
                if not chebi_match.empty:
                    chebi_id = self.get_formula_match(chebi_match, formula, chebi_inchi_id)
            except KeyError as e:
                logger.info("No match to chebi for this lmaps %s", identifier)
                chebi_id = None

        elif identifier.startswith('Std'):
            logger.info("This is a standard DB compound identifer and is no use to chebi ", identifier)
            chebi_id = None
        else:
            logger.warning("We have a new and unusual identifier - do something!!")


        if chebi_id:
            chebi_id = chebi_id[0]


        print ("Returning chebi_id and chebi_inchi_id", chebi_id, chebi_inchi_id)
        return chebi_id, chebi_inchi_id

    def get_formula_match(self, chebi_match, formula, chebi_inchi_id):
        """
        A method to check if the chebi_formula matches the formula that we have in our peak DF
        If a compound returned two different chebi IDS pick the one with the greatest number of identifiers.

        :param chebi_match: Section of DF where the DB ID or inchi matches a row in the Chebi_DF (i.e. it is in the DB)
        :param formula: This is the formula from our peak DF
        :return:
        """
        column_ids = ['kegg_id', 'hmdb_id', 'lmaps_id']
        chebi_id = None

        try:
            formula_match = chebi_match[chebi_match['chebi_formula'] == formula]
            if not formula_match.empty:
                chebi_id = formula_match.chebi_id.values
                if len(chebi_id) > 1:
                    if chebi_inchi_id and (chebi_inchi_id in chebi_id):
                        print ("Chebi_id_inchi and chebi_ids", chebi_inchi_id, chebi_id)
                        # Check if this matches the one of the chebi_inchis
                        chebi_id = [chebi_inchi_id]
                    else:
                        chebi_db_ids = {}
                        # For these chebi ids - count the number of db identifiers and use the chebi_id with the greatest no of identifiers.
                        for c_id in chebi_id:
                            c_id_df = formula_match[formula_match['chebi_id'] == c_id]
                            id_lst = str(c_id_df[column_ids].values[0])
                            no_db_ids = len(column_ids) - id_lst.count('nan')  # No identifiers that are not NaN
                            chebi_db_ids[c_id] = no_db_ids
                        print (chebi_db_ids)
                        chebi_id = [max(chebi_db_ids, key=chebi_db_ids.get)]  # Id with the most identifiers
                        print ("HERE ", chebi_id)


        except KeyError as e:
            print("No match to chebi for this formula ", formula)
            chebi_id = None

        return chebi_id




    def construct_chebi_ontology_df(self):
        """
        This menthod reads the chebi.owl file and produces a df to be used throughout preprocessing
        :return: A DF containing the Chebi ID and all of the matching compound information

        """
        logger.info("Getting the chebi_ontology df")
        try:
            chebi_df = pd.read_pickle("./data/"+CHEBI_DF_NAME+".pkl")
            logger.info("The file %s has been found: ", ADDED_CHEBI_NAME)



        except FileNotFoundError: #If the file is not found then it can be constructed using the code below.

            found_name = False
            new_compound = False
            index = -1

            ontology_groups = ['chebi_id', 'chebi_name', 'chebi_formula', 'chebi_mass', 'chebi_mmass', 'chebi_charge',
                               'hmdb_id', 'kegg_id', 'lmap_id', 'cas_code', 'smiles', 'inchikey']

            chebi_df = pd.DataFrame(columns=ontology_groups)

            with open('/Users/Karen/FlyOmics/notebooks/data/chebi.owl', encoding='utf-8') as f:
                for line in f:
                    # Get the chebi_id
                    if 'owl:Class' in line and 'rdf:about' in line:
                        print (index)
                        index += 1
                        chebi_line = line.strip()
                        res = re.search('CHEBI_(.*)"', chebi_line)
                        chebi = res.group(1)
                        found_name = False  # There are more one line with rdfs_labe so add this to just grab the first one.
                        chebi_df.at[index, 'chebi_id'] = chebi
                        new_compound = True

                    # Get the chebi compound name, more than one label so only take the first (found_name)
                    if 'rdfs:label' in line and not found_name and new_compound:
                        name_line = line.strip()
                        res = re.search('>(.*)<', name_line)
                        name = res.group(1)
                        name = self.escape_names(name)
                        chebi_df.at[index, 'chebi_name'] = name
                        found_name = True

                    # Get the inchikey
                    if 'chebi:inchikey' in line:
                        inchikey_line = line.strip()
                        res = re.search('>(.*)<', inchikey_line)
                        inchikey = res.group(1)
                        chebi_df.at[index, 'inchikey'] = inchikey

                    if 'chebi:formula' in line:
                        formula_line = line.strip()
                        res = re.search('>(.*)<', formula_line)
                        formula = res.group(1)
                        chebi_df.at[index, 'chebi_formula'] = formula

                    if 'chebi:mass' in line:
                        mass_line = line.strip()
                        res = re.search('>(.*)<', mass_line)
                        mass = res.group(1)
                        chebi_df.at[index, 'chebi_mass'] = mass

                    if 'chebi:monoisotopicmass' in line:
                        mmass_line = line.strip()
                        res = re.search('>(.*)<', mmass_line)
                        mmass = res.group(1)
                        chebi_df.at[index, 'chebi_mmass'] = mmass

                    if 'chebi:charge' in line:
                        charge_line = line.strip()
                        res = re.search('>(.*)<', charge_line)
                        charge = res.group(1)
                        chebi_df.at[index, 'chebi_charge'] = charge

                    if 'chebi:smiles' in line:
                        smiles_line = line.strip()
                        res = re.search('>(.*)<', smiles_line)
                        smiles = res.group(1)
                        chebi_df.at[index, 'smiles'] = smiles

                    # Get the HMDB number/ID
                    if 'oboInOwl:hasDbXref' in line and 'HMDB:H' in line:
                        hmdb_line = line.strip()
                        res = re.search('>HMDB:(.*)<', hmdb_line)
                        hmdb = res.group(1)
                        hmdb = self.get_hmdb_no(hmdb)
                        chebi_df.at[index, 'hmdb_id'] = hmdb

                    # Get the Lipid maps ID where possible

                    if 'oboInOwl:hasDbXref' in line and 'LIPID_MAPS_instance:L' in line:
                        lmaps_line = line.strip()
                        res = re.search('>LIPID_MAPS_instance:(.*)<', lmaps_line)
                        lmaps = res.group(1)
                        chebi_df.at[index, 'lmap_id'] = lmaps

                    # Get the KEGG_ID number/ID

                    if 'oboInOwl:hasDbXref' in line and 'KEGG:C' in line:
                        kegg_line = line.strip()
                        res = re.search('>KEGG:(.*)<', kegg_line)
                        kegg = res.group(1)
                        chebi_df.at[index, 'kegg_id'] = kegg

                    # Get the CAS-CODES if availiable

                    if 'oboInOwl:hasDbXref' in line and 'CAS:' in line:
                        cas_line = line.strip()
                        res = re.search('>CAS:(.*)<', cas_line)
                        cas = res.group(1)
                        chebi_df.at[index, 'cas_code'] = cas

            try:
                chebi_df.to_pickle("./data/" + CHEBI_DF_NAME + ".pkl")
            except Exception as e:
                logger.error("Pickle didn't work because of %s ", e)
                pass

        return chebi_df


    def get_hmdb_no(self, identifier):
        """
        Method to get the HMDB number as the identifier as the identifiers between PiMP and CheBi don't match.
        """
        p = re.compile('HMDB0*(\d+)')
        m = p.match(identifier)
        hmdb_no = m.group(1)

        return hmdb_no

    def escape_names(self, name):
        """
        A method to replace the special characters returned by the chebi Owl file in the compound names
        :return: The cmpd name with the escape characters replaced.
        """

        html_escape_table = {
            "&amp;": "&",
            "&quot;": '"',
            "&apos;": "'",
            "&gt;": ">",
            "&lt;": "<",
        }

        for k, v in html_escape_table.items():
            if k in name:
                name = name.replace(k, html_escape_table[k])
        return name