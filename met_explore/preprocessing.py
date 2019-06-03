import pandas as pd
import re
import numpy as np
import logging
logger = logging.getLogger(__name__)

# Names to pickle the files as we go along so canges can be made without running all of the methods again.
CHEBI_DF_NAME = "chebi_ontology_df2"
ADDED_CHEBI_NAME = "chebi_peak_df_1"
CHEBI_CMPD_MATCH = "chebi_peak_df_cmpd_match_1"
CHEBI_UNIQUE_IDS = "chebi_unique_cmpd_ids_2"

class PreprocessCompounds(object):
    """
    This is a class to preproccess the compounds and give them unique Chebi IDS
    """

    def __init__(self, peak_json_file):

        self.peak_json_file = peak_json_file
        self.chebi_df = self.get_chebi_ontology_df()
        self.peak_df = pd.read_json(self.peak_json_file)


    def get_preprocessed_cmpds(self):


        self.add_chebi_ids()
        self.give_each_chebi_same_id()
        self.give_chebi_inchi_unique_id()


    def add_chebi_ids(self):
        """
        Method to add Chebi IDS to our peak list DF for all of the compounds.
        :return:
        """
        logger.info("Adding the chebi_ids")
        try:
            self.peak_df = pd.read_pickle("./data/" + ADDED_CHEBI_NAME + ".pkl")  # KMCL - this file should be named after the input files so not to repeat.
            print("WE have the DF", self.peak_df.head())

        except FileNotFoundError:

            self.peak_df["chebi_id"] = None # Add empty column to fill in.
            self.peak_df["chebi_name"] = None

            for index, row in self.peak_df.iterrows():

                set_chebi_id = row.chebi_id
                identifier = row.identifier
                inchi = row.inchikey
                formula = row.formula

                if not set_chebi_id:
                    logger.info("The identifier/inchi/formula are ", identifier, inchi, formula)

                    chebi_id, chebi_id_inchi = self.get_chebi_id(identifier, inchi, formula)

                    # If both exist add the chebi_id (based on the DB identifier) to the DF
                    if chebi_id and chebi_id_inchi:
                        logger.info("The ID and chebi_id are both found: ", chebi_id, chebi_id_inchi)
                        logger.info("Adding the chebi_id", chebi_id)

                        self.peak_df.loc[index, 'chebi_id'] = chebi_id

                        # Get the chebi inchi if it exists & If it's not null add it to the DF.
                        inchi = self.chebi_df[self.chebi_df.chebi_id == chebi_id].inchikey.values[0]
                        if not pd.isnull(inchi):
                            self.peak_df.loc[index, 'inchikey'] = inchi

                    elif chebi_id and not chebi_id_inchi:
                        logger.info('chebi_id and not chebi_id_inchi, adding ', chebi_id)
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

            ## Add Chebi names to the peak DF
            for index, row in self.peak_df.iterrows():
                if row.chebi_id:  # If not a null value
                    chebi_id = row.chebi_id
                    chebi_name = self.chebi_df[self.chebi_df.chebi_id == chebi_id].chebi_name.values[
                        0]
                    print(chebi_id, chebi_name)
                    self.peak_df.loc[index, 'chebi_name'] = chebi_name

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
            print("WE have the DF", self.peak_df.head())

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
            print("WE have the DF", self.peak_df.head())

        except FileNotFoundError:
            max_cmpd_id = self.peak_df['cmpd_id'].max()

            cmpd_ids = self.peak_df.cmpd_id.unique()
            for cmpd in cmpd_ids:

                single_cmpd_df = self.peak_df[self.peak_df['cmpd_id'] == cmpd]
                indexes = single_cmpd_df.index.values

                cmpd_ids = single_cmpd_df.cmpd_id.unique()
                no_cmpd_ids = len(cmpd_ids)
                inchi_keys = single_cmpd_df.inchikey.unique()
                no_inchi_keys = len(inchi_keys)
                # no_present_inchi = sum(1 for _ in filter(None.__ne__, inchi_keys))
                present_inchis = inchi_keys[inchi_keys != np.array(None)]

                # identifiers = single_cmpd_df.identifier.unique()
                # no_identifiers = len(identifiers)
                chebi_ids = single_cmpd_df.chebi_id.unique()

                present_chebi_ids = chebi_ids[chebi_ids != np.array(None)]


                formulas = (single_cmpd_df.formula.unique())
                no_formulas = len(formulas)

                # Same compound IDs, different CheBi_ids - give the row a new cmpd_id = Max cmpd_id +1
                if len(present_chebi_ids) > 1:  # If the inchi keys are 1 and None just leave.

                    logger.info("This compound id %S has more than one inchi_key %S",cmpd, chebi_ids )

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

                # Same compound IDs but different formulas
                if no_formulas > 1 :
                    logger.info("This compound id %S has more than one inchi_key %S",cmpd, formulas )
                    for f in formulas[1:]: #Keep the first formula, change the rest
                        max_cmpd_id +=1
                        scmpd_id_df = single_cmpd_df[single_cmpd_df.formula==f]
                        change_indexes = scmpd_id_df.index.values
                        self.peak_df.loc[change_indexes,'cmpd_id']= max_cmpd_id

                # Check for dulicate inchikeys
                if len(present_inchis) > 1: # If the inchi keys are 1 and None just leave alone - more than one non null value
                    logger.info("This compound id %S has more than one inchi_key %S",cmpd, inchi_keys )
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

        if identifier.startswith('C'):  # Kegg identifier
            try:
                chebi_match = self.chebi_df[self.chebi_df['kegg_id'] == identifier]
                if not chebi_match.empty:
                    chebi_id = self.get_formula_match(chebi_match, formula)

            except KeyError as e:
                logger.info("No match to chebi for this kegg id ", identifier)
                chebi_id = None

        elif identifier.startswith('HMDB'):
            hmdb_no = self.get_hmdb_no(identifier)
            try:
                chebi_match = self.chebi_df[self.chebi_df['hmdb_id'] == hmdb_no]
                if not chebi_match.empty:
                    chebi_id = self.get_formula_match(chebi_match, formula)
            except KeyError as e:
                logger.info("No match to chebi for this hmdb id ", identifier)
                chebi_id = None

        elif identifier.startswith('LM'):
            try:
                chebi_match = self.chebi_df[self.chebi_df['lmaps_id'] == identifier]
                if not chebi_match.empty:
                    chebi_id = self.get_formula_match(chebi_match, formula)
            except KeyError as e:
                logger.info("No match to chebi for this lmaps ", identifier)
                chebi_id = None

        elif identifier.startswith('Std'):
            logger.info("This is a standard DB compound identifer and is no use to chebi ", identifier)
            chebi_id = None
        else:
            logger.warning("We have a new and unusual identifier - do something!!")

        # Get the chebi_id based on Inchi - hopefully when found it matches the one on ID.
        if inchikey is not None:

            logger.info("Trying to get Chebi on Inchi")
            try:
                chebi_match = self.chebi_df[self.chebi_df['inchikey'] == inchikey]
                if not chebi_match.empty:
                    chebi_inchi_id = self.get_formula_match(chebi_match, formula)

            except KeyError as e:
                logger.info("No match to chebi for this inchi ", inchikey)
                chebi_inchi_id = None
                # Return the value and not the array

        if chebi_id:
            chebi_id = chebi_id[0]

        if chebi_inchi_id:
            chebi_inchi_id = chebi_inchi_id[0]

        logger.info("Returning chebi_id and chebi_inchi_id ", chebi_id, chebi_inchi_id)
        return chebi_id, chebi_inchi_id

    def get_formula_match(self, chebi_match, formula):
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
                    chebi_db_ids = {}
                    # For these chebi ids - count the number of db identifiers and use the chebi_id with the greatest no of identifiers.
                    for c_id in chebi_id:
                        c_id_df = formula_match[formula_match['chebi_id'] == c_id]
                        id_lst = str(c_id_df[column_ids].values[0])
                        no_db_ids = len(column_ids) - id_lst.count('nan')  # No identifiers that are not NaN
                        chebi_db_ids[c_id] = no_db_ids
                        chebi_id = max(chebi_db_ids, key=chebi_db_ids.get)  # Id with the most identifiers

        except KeyError as e:
            print("No match to chebi for this formula ", formula)
            chebi_id = None

        return chebi_id




    def get_chebi_ontology_df(self):
        """
        This menthod reads the chebi.owl file and produces a df to be used throughout preprocessing
        :return: A DF containing the Chebi ID and all of the matching compound information

        """

        try:
            chebi_df = pd.read_pickle("./data/chebi_ontology_df2.pkl")

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
                        index += 1
                        chebi_line = line.strip()
                        res = re.search('CHEBI_(.*)"', chebi_line)
                        chebi = res.group(1)
                        logger.info("Adding details for the index and chebi code:", index, chebi)
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