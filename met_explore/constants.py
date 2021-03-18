CSV_GROUP_COLNAME = 'group'
FACTOR_ORDER_DICT = {'primary_factor': ['tissue', 'age'], 'secondary_factor': ['life_stage']}
FACTOR_DISPLAY_NAME = {
    'F': 'Adult Female FC',
    'M': 'Adult Male FC',
    'L': 'Larvae FC'
}
METABOLITE_EXPLORER = 'metabolite_explorer'

SPECIES = 'Drosophila'
UI_CONFIG = {
    SPECIES: SPECIES,
    METABOLITE_EXPLORER: [
        {
            'category': 'Tissues',
            'analysis': 'Tissue Comparisons',
            'msg_search': 'Search for a <b>metabolite</b> and find out the abundance in <i> {species} </i> tissues',
            'msg_table_title': '{metabolite} levels in <i> {species} </i> tissues',
            'msg_sidebar': 'Click on a tissue-type to see the intensities of the peaks associated with {metabolite}'
        },
        {
            'category': 'Age',
            'analysis': 'Age Comparisons',
            'msg_search': 'Search for a <b>metabolite</b> and find out the abundance in different ages of <i> {species} </i>.',
            'msg_table_title': '{metabolite} levels in different aged <i> {species} </i>',
            'msg_sidebar': 'Click on an age to see the intensities of the peaks associated with {metabolite}'
        }
    ]
}
