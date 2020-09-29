import json

import numpy as np
from django.db import IntegrityError
from loguru import logger
from tqdm import tqdm

from met_explore.pathway_analysis import get_chebi_relation_dict
from met_explore.serializers import SampleSerializer, Peak, Compound, DBNames, CompoundDBDetails, Annotation, Sample, \
    SamplePeakSerializer


def populate_samples(sample_csv):
    '''
    Give the sample CSV file to populate the samples.
    KMcL: Working but need to consider the filepath.
    '''
    sample_details = np.genfromtxt(sample_csv, delimiter=',', dtype=str)[2:]
    logger.debug("sd_type %s" % sample_details)
    for sample in sample_details:
        # sample = s.split()
        sample_serializer = SampleSerializer(
            data={"name": sample[0], "group": sample[1], "life_stage": sample[2], "tissue": sample[3],
                  "mutant": sample[4]})
        if sample_serializer.is_valid():
            db_sample = sample_serializer.save()
            logger.debug("sample saved %s" % db_sample.name)
        else:
            logger.debug(sample_serializer.errors)


# This requires the input taken from the construct_peak_df method/
# It requires all secondary_ids to be unique and reports any errors (throw?)
# To get the list and dict back from the json.dumps just use json.loads
# This has been refactored to populate Peak, Annotation and Compound models.


def populate_peaks_cmpds_annots(peak_df):
    """

    :param peak_df: A dataframe of filtered peaks from the peak_selector based on adducts, identification, fragmentation
    -it also ony returns a single peak (single sec_id from PiMP)
    :return: Populates the peaks, compounds and annotations for the filtered peaks.
    """

    # For each row of the DF grab the peak, compound and annotation that relates them.
    logger.info('Populating peak, compound and annotation database')
    for index, row in tqdm(peak_df.iterrows(), total=peak_df.shape[0]):

        # Populating the peak
        logger.debug("We are populating row %s" % index)
        db_peak, peak_created = Peak.objects.get_or_create(psec_id=row.sec_id, m_z=format(row.mass, '.9f'),
                                                           rt=format(row.rt, '.9f'), polarity=row.polarity)

        if peak_created:
            logger.debug("A new peak %s was created %s" % (db_peak, peak_created))
            db_peak.save()

        # Populating the compound and it's DB entries from the row.
        # Get or create the compound associated with the peak
        try:
            store_cmpd, cmpd_created = Compound.objects.get_or_create(pc_sec_id=row.cmpd_id, cmpd_formula=row.formula,
                                                                      chebi_id=row.chebi_id, chebi_name=row.chebi_name,
                                                                      smiles=row.smiles, cas_code=row.cas_code,
                                                                      inchikey=row.inchikey)
            if cmpd_created:
                store_cmpd.save()

        # Special case when two different rows returned for the same compound.
        except IntegrityError as e:
            logger.debug("different row same cmpd_id, chebi_id")

            store_cmpd, cmpd_created = Compound.objects.get_or_create(pc_sec_id=row.cmpd_id, cmpd_formula=row.formula,
                                                                      chebi_id=row.chebi_id, chebi_name=row.chebi_name)

            if not cmpd_created:
                if store_cmpd.smiles == 'nan' and row.smiles:
                    store_cmpd.smiles = row.smiles
                    store_cmpd.save()
                if store_cmpd.cas_code == 'nan' and row.cas_code:
                    store_cmpd.cas_code = row.cas_code
                    store_cmpd.save()
                if not store_cmpd.inchikey and row.inchikey:
                    store_cmpd.inchikey = row.inchikey
                    store_cmpd.save()

        # For the lists if names, ids, and databases create the CompoundDBDetails objects.
        for db_name, dbid, name in zip(row.db, row.identifier, row['compound']):

            store_db_name, store_dbname_created = DBNames.objects.get_or_create(db_name=db_name)

            if store_dbname_created:
                logger.debug("Saving the DB name object %s " % (store_db_name))
                store_db_name.save()

            # Assuming we just want to create a new compound DB details entry for each compound
            store_cmpd_details, created_cmpd_details = CompoundDBDetails.objects.get_or_create(db_name=store_db_name,
                                                                                               identifier=dbid,
                                                                                               cmpd_name=name,
                                                                                               compound=store_cmpd)

            if created_cmpd_details:
                logger.debug("New cmpd details were created %s" % (store_cmpd_details))
                store_cmpd_details.save()

        # Populating the Annotation to relate the peak to the compound and vice-versa
        frank_annot = json.dumps(row.frank_annot)
        stored_annot, created_annot = Annotation.objects.get_or_create(compound=store_cmpd, peak=db_peak,
                                                                       identified=row.identified,
                                                                       neutral_mass=format(row.neutral_mass, '.9f'),
                                                                       frank_anno=frank_annot, adduct=row.adduct)

        if created_annot:
            logger.debug("Storing the annotation %s" % stored_annot)
            stored_annot.save()

    logger.info("The filtered peaks, compounds and annotations have been populated")


def add_related_chebis():
    """
    Method to add the related chebi ids from Reactome to the compounds.
    :return:
    """
    logger.info('Add related Chebis')
    compounds = Compound.objects.all()
    for c in tqdm(compounds):
        if c.chebi_id:
            related_chebi = get_related_chebis(c.chebi_id)
            if related_chebi:
                c.related_chebi = related_chebi
                c.save()


def get_related_chebis(chebi_id):
    """
    A method to return related Chebi_IDs - these are alternative Chebis for acid/base conjugates and tautomers used by Reactome.
    :param chebi_id:
    :return: related_chebi_ids
    """

    chebi_rel_dict = get_chebi_relation_dict()
    if chebi_id in chebi_rel_dict.keys():

        related_chebis = chebi_rel_dict[chebi_id]

    else:
        related_chebis = None

    return related_chebis


# Takes a peak intensity DF and a pimp peak id / secondary id dictionary to populate the PeakSamples.
# The dictionary is passed in as the Peak model only stores the psec id and not the pid from PiMP.

def populate_peaksamples(intensity_df, pids_sids_dict):
    logger.info('Populate peak samples')

    columns = list(intensity_df.columns)
    for i in range(len(columns)):
        col = columns[i]
        logger.info('Processing %d/%d: %s' % (i, len(columns), col))
        sample = Sample.objects.get(name=col)
        this_col = intensity_df[col]

        # Get the data for the SamplePeak
        # for index, value in this_col.iteritems():
        for index, value in tqdm(this_col.iteritems(), total=this_col.shape[0]):
            sec_id = pids_sids_dict[index]
            intensity = value
            peak = Peak.objects.get(psec_id=sec_id)
            logger.debug("we are adding the data for: %s %s %f " % (sample, peak, intensity))

            # Populate the DB
            samplepeak_serializer = SamplePeakSerializer(
                data={"peak": peak.id, "sample": sample.id, "intensity": intensity})
            if samplepeak_serializer.is_valid():
                db_samplepeak = samplepeak_serializer.save()
                logger.debug("peak saved %s" % db_samplepeak.peak)
            else:
                logger.warning(samplepeak_serializer.errors)
