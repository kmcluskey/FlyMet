from met_explore.pathway_analysis import *
from django.core.cache import cache
from loguru import logger

from pyMultiOmics.constants import *
from pyMultiOmics.mapping import Mapper
from pyMultiOmics.analysis import *
from pyMultiOmics.query import *
from pyMultiOmics.pipelines import *
from pyMultiOmics.common import set_log_level_info


try:
    DATA_FOLDER = os.path.abspath(os.path.join('.', 'omics_data'))
    flyatlas_filename = os.path.join(DATA_FOLDER, 'FlyAtlas2_Alltissues_Allgenes.csv')
    fly_atlas2_df = pd.read_csv(flyatlas_filename, encoding = 'unicode_escape', index_col='FlyBaseID')
except FileNotFoundError:
    logger.warning('FlyAtlas gene data not found at %s' % flyatlas_filename)

class MultiOmics(object):
    """
    A class that contains various methods for use when running multi-omics for a specific analysis
    """

    def __init__(self, analysis):

        self.DATA_FOLDER = os.path.abspath(os.path.join('.', 'omics_data'))
        self.fly_atlas2_df = pd.read_csv(os.path.join(self.DATA_FOLDER, 'FlyAtlas2_Alltissues_Allgenes.csv'),
                                    encoding='unicode_escape', index_col='FlyBaseID')

        self.analysis = analysis
        self.ap =  self.get_cache_ap() # Analysis_pipeline

    def get_cache_ap(self):
        a_id = str(self.analysis.id)
        cache_name = 'ap_' + a_id

        # cache.delete(cache_name)
        if cache.get(cache_name) is None:
            logger.info("we dont have cache so running the ap function")
            cache.set(cache_name, self.get_analysis_pipeline(), 60 * 180000)
            ap = cache.get(cache_name)
        else:
            logger.info("we have cache for the ap so retrieving it")
            ap = cache.get(cache_name)

        return ap


    def get_analysis_pipeline(self):

        ## Currently the gene data and design were just produced by hand from the flyatlas data
        gene_data = pd.read_csv(os.path.join(self.DATA_FOLDER, 'flyatlas_data.csv'), index_col='Identifier')
        gene_design = pd.read_csv(os.path.join(self.DATA_FOLDER, 'flyatlas_design.csv'), index_col='sample')

        compound_data = self.get_cache_omics_df()
        compound_design = self.get_omics_design()

        set_log_level_info()

        m = Mapper(DROSOPHILA_MELANOGASTER, metabolic_pathway_only=True, include_related_chebi=True) \
            .set_gene(gene_data, gene_design) \
            .set_compound(compound_data, compound_design) \
            .build()

        ap = AnalysisPipeline(m)

        return ap

    def test_omics(self, query_list):

        gene_protein = QueryBuilder(self.ap) \
            .add(Entity(query_list)) \
            .add(Connected()) \
            .run()

        return gene_protein


    def get_cache_omics_df(self):

        a_id = str(self.analysis.id)
        # cache.delete('omics_df'+a_id)
        cache_name = 'omics_ds'+a_id

        if cache.get(cache_name) is None:
            logger.info("we dont have cache so running the omics_df function")
            cache.set(cache_name, self.get_omics_df(), 60 * 180000)
            omics_df = cache.get(cache_name)
        else:
            logger.info("we have cache for the omics_df, so retrieving it")
            omics_df = cache.get(cache_name)
        return omics_df


    def get_omics_df(self):

        """
        This method returns a DF suitable for pyMultiOmics where one Chebi id is associated with a single peals
        The high confidence peaks in the DB are selected by their
        confidence factor and the other compunds simply on the average max max intenity of their peaks.

        :param: analysis - the analysis for which the samples are required for the omics experiment.
        :return: DF of chebi_id followed by individual samples and their peak intensities
        """

        fly_annot_df = get_cache_annot_df()

        # Insert the confidence values as a column
        conf_facts = list(Annotation.objects.values_list('confidence', flat=True))
        fly_annot_df.insert(0, 'confidence', conf_facts)

        # Remove all rows where chebi_id is none
        fly_annot_df = fly_annot_df[fly_annot_df['chebi_id'].notnull()]

        # Select only required columns
        fly_annot_df = fly_annot_df[['confidence', 'peak_ids', 'chebi_id']]

        # Get a dataframe for the high confidence peaks only.
        hc_df = fly_annot_df[(fly_annot_df['confidence'] == 4) | (fly_annot_df['confidence'] == 3)]

        # List of high confidence chebis and peak_ids
        hc_df_chebi = list(hc_df.chebi_id.values)
        hc_peak_ids = list(hc_df.peak_ids.values)

        # Remove all the rows from the DF where the the chebi_id and peak_id is in the Hc_df
        fly_filtered_df = fly_annot_df[(~fly_annot_df['chebi_id'].isin(hc_df_chebi)) & \
                                       (~fly_annot_df['peak_ids'].isin(hc_peak_ids))]

        # Add back the high confidence dataframe.
        chebi_peak_df = fly_filtered_df.append(hc_df)

        chebi_peak_df = chebi_peak_df[['peak_ids', 'chebi_id']].set_index('peak_ids')

        ### The pals_int_df gives the peak intensities for all samples in an analysis

        pals_int_df = get_pals_int_df(self.analysis)

        combined_df = chebi_peak_df.combine_first(pals_int_df)
        combined_df = combined_df.set_index('chebi_id')
        combined_df = combined_df[combined_df.index.notnull()]
        combined_df.index.name = 'Identifier'
        combined_df = combined_df.reset_index()

        final_df = self.remove_dupes(combined_df)
        final_df = final_df.set_index("Identifier")

        return final_df


    def get_omics_design(self):
        """

        :param analysis: Analysis for the samples and groups requires
        :return: DF with sample name as index and groups for the columns.
        """

        fly_exp_design = get_pals_experimental_design(self.analysis)
        groups = fly_exp_design['groups']
        df_design = pd.DataFrame([(var, key) for (key, slist) in groups.items() for var in slist],
                                 columns=['sample', 'group'])
        df_design = df_design.set_index('sample')

        return df_design


    def remove_dupes(self, df):
        """
        :param df: A dataframe with an Identifier column and intensity data.
        :return: The same dataframe with one row per identifier - with the row chosen of max sum of intensities
        across the row. Duplicate rows deleted.
        """
        # df = df.reset_index()

        # group df by the 'Identifier' column
        to_delete = []
        grouped = df.groupby(df['Identifier'])
        for identifier, group_df in grouped:

            # if there are multiple rows sharing the same identifier
            if len(group_df) > 1:
                # remove 'Identifier' column from the grouped df since it can't be summed
                group_df = group_df.drop('Identifier', axis=1)

                # find the row with the largest sum across the row in the group
                idxmax = group_df.sum(axis=1).idxmax()

                # mark all the rows in the group for deletion, except the one with the largest sum
                temp = group_df.index.tolist()
                temp.remove(idxmax)
                to_delete.extend(temp)

        # actually do the deletion here
        logger.info('Removing %d rows with duplicate identifiers' % (len(to_delete)))
        df = df.drop(to_delete)
        # df = df.set_index(IDENTIFIER_COL)
        return df


    def get_single_entity_relation(self, entities, relation=None):
        """
        Returns the mapping DF for a certain relation eg. Pathways, or ALL if relation is not passed.
        :param entities: List. The entities that you want to map from eg. Compound (entity)---> Pathway (relation)
        :param relation: List: The relational results required e.g is you want Pathways (relation) associate with compounds (entity)
        :param ap: The pyMultiOmics analysis pipeline.
        :return: A DF with all the required relations.
        """

        mapping_df = QueryBuilder(self.ap) \
            .add(Entity(entities)) \
            .add(Connected()) \
            .run()

        if relation is not None:
            relation_df = mapping_df[mapping_df.data_type.isin([relation])]
        else:
            relation_df = mapping_df

        return relation_df


    def get_fbgn_codes(self, genes):
        """
        :param genes: The annotation codes for genes
        :return: A list of fbgn codes that we can use in Reactome.
        """

        fb_genes = []
        for gene in genes:
            fb_id = self.fly_atlas2_df[self.fly_atlas2_df.Annotation == gene].index.tolist()
            fb_genes.extend(fb_id)

        return fb_genes


    def get_cache_gene_df(self):

        a_id = str(self.analysis.id)
        # cache.delete('omics_df'+a_id)
        cache_name = 'gene_df' + a_id

        if cache.get(cache_name) is None:
            logger.info("we dont have cache so getting the gene_df")
            cache.set(cache_name, self.get_gene_df(), 60 * 180000)
            gene_df = cache.get(cache_name)
        else:
            logger.info("we have cache for the gene_df so retrieving it")
            gene_df = cache.get(cache_name)

        return gene_df

    def get_gene_df(self):

        flybase_ids = self.fly_atlas2_df.index.values

        all_genes = QueryBuilder(self.ap) \
            .add(Entity(flybase_ids)) \
            .add(Connected()) \
            .run()

        unique_mapped_genes = all_genes.source_id.unique()
        mapped_flyatlas = self.fly_atlas2_df[self.fly_atlas2_df.index.isin(unique_mapped_genes)]
        mapped_flyatlas = mapped_flyatlas[["Name", "Annotation", "Symbol"]]

        return mapped_flyatlas
