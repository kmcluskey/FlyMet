import json

import pandas as pd
from django.db import IntegrityError
from loguru import logger
from tqdm import tqdm

from met_explore.constants import CSV_GROUP_COLNAME
from met_explore.models import Peak, Compound, DBNames, CompoundDBDetails, Annotation, Sample, Factor, SamplePeak,\
Group, Analysis, AnalysisComparison, Project, Category


from met_explore.pathway_analysis import get_related_chebi_ids


def populate_samples(sample_csv):
    '''
    Give the sample CSV file to populate the samples.
    '''

    # Read sample csv
    # Assume the first column is the sample
    # Drop empty rows where it's all NaN if they're present
    sample_details = pd.read_csv(sample_csv, index_col=0).dropna(how='all')

    # Assume other columns are the experimental factors
    factor_names = sample_details.columns.values
    assert CSV_GROUP_COLNAME in factor_names, 'Missing group information in CSV'

    for idx, row in sample_details.iterrows():
        try:
            # save sample and the group column
            sample_name = idx.strip()

            group_name = row[CSV_GROUP_COLNAME]
            group, group_created = Group.objects.get_or_create(name=group_name)
            if group_created:
                group.save()
            sample = Sample(name=sample_name, group=group)
            sample.save()

            # save other columns as factors
            for factor_name in factor_names:
                if factor_name == CSV_GROUP_COLNAME: # skip the group column as it has been saved
                    continue
                factor_value = row[factor_name]
                factor, factor_created = Factor.objects.get_or_create(group=group, type=factor_name, name=factor_value)
                if factor_created:
                    factor.save()
                    logger.info("saving factor %s " % factor )

        except IntegrityError as e:
            logger.warning('Samples %s have been inserted, skipping, check input for duplicates' % sample)
            continue

    logger.info('All samples loaded to database')


def populate_analysis_comparisions(analysis_set):
    """
    :param analysis_set: JSON file containing all the analysis and comparisons information for a project
    :return: populate the Analysis and AnalysisComparison objects
    """

    logger.info('Populating the analysis_set and comparisons')

    f = open(analysis_set,)
    x = f.read()

    config_dict = json.loads(x)
    projects = config_dict["projects"]

    for project in projects:
        try:
            new_project, project_created =Project.objects.get_or_create(name=project["project_name"], description=project["project_description"])
            if project_created:
                new_project.save()
                logger.info("Saving the project for %s" % new_project)

                metabolomics = project['metabolomics']
                project_categories = metabolomics['categories']

                for category in project_categories:
                    new_category, category_created = Category.objects.get_or_create(name=category['category_name'], description = category['description'], project = new_project)
                    if new_category:
                        new_category.save()
                        logger.info("Saving the category for %s" % new_category)

                    analysis_sets = category['analysis_sets']

                    for analysis in analysis_sets:

                        new_analysis, analysis_created = Analysis.objects.get_or_create(name=analysis["analysis_name"], type=analysis["analysis_type"], category=new_category)
                        if analysis_created:
                            new_analysis.save()
                            logger.info("Saving the analysis and comparisons for %s" % new_analysis)

                            comparisons = analysis["comparisons"]
                            for c in comparisons:
                                comp_case = Group.objects.get(name=c['case'])
                                comp_control = Group.objects.get(name=c['control'])
                                comparison = AnalysisComparison(analysis = new_analysis, name=c['comparison_name'], case_group=comp_case, control_group=comp_control)
                                comparison.save()
                                logger.info("Saving the comparison for %s" % comparison)


        except IntegrityError as e:
            logger.warning(e)
            raise
    logger.info('Analysis_set population complete')

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
    logger.info('Adding related Chebis')
    compounds = Compound.objects.all()
    for c in tqdm(compounds):
        if c.chebi_id:
            r_chebi = get_related_chebi_ids([c.chebi_id])
            related_chebi = ', '.join(r_chebi)
            if related_chebi:
                c.related_chebi = related_chebi
                c.save()


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
        data = []
        for index, value in tqdm(this_col.iteritems(), total=this_col.shape[0]):
            sec_id = pids_sids_dict[index]
            intensity = value
            peak = Peak.objects.get(psec_id=sec_id)
            logger.debug("we are adding the data for: %s %s %f " % (sample, peak, intensity))
            sample_peak = SamplePeak(peak=peak, sample=sample, intensity=intensity)
            data.append(sample_peak)

        # Populate the DB
        SamplePeak.objects.bulk_create(data)