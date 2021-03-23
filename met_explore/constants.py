CSV_GROUP_COLNAME = 'group'
FACTOR_ORDER_DICT = {'primary_factor': ['tissue', 'age'], 'secondary_factor': ['life_stage']}
SEARCH_SECTIONS = 'search_sections'
INITIAL_ANALYSIS = 'entry_analysis'
SPECIES = 'Drosophila'
UI_CONFIG = {
    SPECIES: SPECIES,
    INITIAL_ANALYSIS: 'Tissue Comparisons',
    SEARCH_SECTIONS: [
        {
            'analysis': 'Tissue Comparisons',
            'colnames': {
                'F': 'Adult Female FC',
                'M': 'Adult Male FC',
                'L': 'Larvae FC'
            }
        },
        {
            'analysis': 'Age Comparisons',
            'colnames': {
                'F': 'Adult F/W p-value',
                'M': 'Adult M/W p-value',
                'L': 'Larvae/W p-value'
            }
        }
    ]
}
