CSV_GROUP_COLNAME = 'group'
FACTOR_ORDER_DICT = {'primary_factor': ['tissue', 'age'], 'secondary_factor': ['life_stage']}
FACTOR_DISPLAY_NAME = {
    'F': 'Adult Female FC',
    'M': 'Adult Male FC',
    'L': 'Larvae FC'
}
SEARCH_SECTIONS = 'search_sections'
INITIAL_ANALYSIS = 'entry_analysis'
SPECIES = 'Drosophila'
UI_CONFIG = {
    SPECIES: SPECIES,
    INITIAL_ANALYSIS: 'Tissue Comparisons',
    SEARCH_SECTIONS: [
        {
            'analysis': 'Tissue Comparisons',
        },
        {
            'analysis': 'Age Comparisons',
        }
    ]
}
