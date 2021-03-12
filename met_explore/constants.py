CSV_GROUP_COLNAME = 'group'
FACTOR_ORDER_DICT = {'primary_factor': ['tissue', 'age'], 'secondary_factor': ['life_stage']}
METABOLITE_EXPLORER = 'metabolite_explorer'

UI_CONFIG = {
    METABOLITE_EXPLORER: [
        {
            'category': 'Tissues',
            'analysis': 'Tissue Comparisons',
            'msg_search': 'Search for a <b>metabolite</b> and find out the abundance in <i> Drosophila </i> tissues',
            'msg_table_title': '{metabolite} levels in <i> Drosophila </i> tissues'
        },
        {
            'category': 'Age',
            'analysis': 'Age Comparisons',
            'msg_search': 'Search for a <b>metabolite</b> and find out the abundance in different ages of <i> Drosophila </i>.',
            'msg_table_title': '{metabolite} levels in different aged <i> Drosophila </i>'
        }
    ]
}
