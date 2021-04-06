CSV_GROUP_COLNAME = 'group'
FACTOR_ORDER_DICT = {'primary_factor': ['PyMT'], 'secondary_factor': None}
SEARCH_SECTIONS = 'search_sections'
INITIAL_ANALYSIS = 'entry_analysis'
SPECIES = 'Mouse'
UI_CONFIG = {
    SPECIES: SPECIES,
    INITIAL_ANALYSIS: 'Metastasis Comparisons',
    SEARCH_SECTIONS: [
        {
            'analysis': 'Metastasis Comparisons',
            'colnames': {
                'HighMet': 'High Metastasis',
                'LowMet': 'Low Metastatis',
            },
            'case_label': 'mice with high number of tumours',
            'control_label': 'mice with low number of tumours'
        },
    ]
}
