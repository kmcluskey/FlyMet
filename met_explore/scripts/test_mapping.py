from met_explore.multi_omics import MultiOmics
from met_explore.models import Analysis

# Use python manage.py runscript test_mapping to return the shape of the gene_df
# If this is a new run remember to delete the cache for get_cache_gene_df()

def run():
	analysis_tissue = Analysis.objects.get(name="Tissue Comparisons")
	mo_tissue = MultiOmics(analysis_tissue)

	gene_df = mo_tissue.get_cache_gene_df()

	print ("The shape of the gene df is: ")
	print (gene_df.shape)