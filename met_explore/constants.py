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
                'F': 'Adult Female',
                'M': 'Adult Male',
                'L': 'Larvae'
            },
            'case_label': 'tissues in adult Male (M), adult Female (F) or larvae (L)',
            'control_label': 'Whole Fly'
        },
        {
            'analysis': 'Age Comparisons',
            'colnames': {
                'F': 'Adult Female',
                'M': 'Adult Male',
                'L': 'Larvae'
            },
            'case_label': 'ages in adult Male (M), adult Female (F) or larvae (L)',
            'control_label': 'Whole Fly (7 days old)'
        }
    ]
}
