import json
import math
import timeit

import django
import numpy as np
import pandas as pd
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from loguru import logger

from met_explore.compound_selection import CompoundSelector, HC_INTENSITY_FILE_NAME
from met_explore.constants import UI_CONFIG, SEARCH_SECTIONS, SPECIES, INITIAL_ANALYSIS
from met_explore.helpers import natural_keys, get_control_from_case, get_group_names, get_factor_type_from_analysis, \
    get_factors_from_samples, get_ui_config, get_initial_analysis_from_config, get_display_colnames, \
    get_search_categories
from met_explore.models import Peak, CompoundDBDetails, Compound, Sample, Annotation, Analysis, AnalysisComparison, \
    Group, Factor, Category
from met_explore.pathway_analysis import get_pathway_id_names_dict, get_highlight_token, get_cache_df, \
    get_fly_pw_cmpd_formula, get_cmpd_pwys, get_name_id_dict, MIN_HITS
from met_explore.peak_groups import PeakGroups

# from met_explore.forms import ContactForm

MIN = -7
MAX = 7
MEAN = 0

NUM_WHOLE_SAMPLES = 12
WF_MIN = 1000  # Minimum value used for missing values in the whole fly data.

# If the Db exists and has been initialised:
try:
    cmpd_selector = CompoundSelector()
    # DFs for all the peaks
    # int_df = cmpd_selector.construct_cmpd_intensity_df()
    # peak_group_int_df =  cmpd_selector.get_group_df(int_df)

    # DF for the Highly confident peaks
    hc_int_df = cmpd_selector.get_hc_int_df()
    s_cmpds_df = cmpd_selector.get_single_cmpd_df(hc_int_df)
    single_cmpds_df = s_cmpds_df.reindex(sorted(s_cmpds_df.columns[1:]), axis=1)
    single_cmpds_df.insert(0, "Metabolite", s_cmpds_df['Metabolite'])

except django.db.utils.OperationalError as e:

    logger.warning("I'm catching this error %s " % e)

    logger.warning("DB not ready, start server again once populated")
    cmpd_selector = None

except FileNotFoundError as e:

    logger.error("Please reinitialise DB and make sure the file exists /data/%s.pkl" % HC_INTENSITY_FILE_NAME)
    logger.info("Returning the DF as None")

    cmpd_selector = None

except Exception as e:
    logger.warning("I'm catching this error %s" % e)
    logger.warning("Hopefully just that the DB not ready, start server again once populated")
    raise e


def index(request):
    # return HttpResponse("Hello, world. You're at the met_explore index page.")
    analysis = get_initial_analysis_from_config(UI_CONFIG)
    all_categories = get_search_categories(UI_CONFIG)
    context = {
        'json_url': reverse('get_metabolite_names'),
        'analysis_id': analysis.id,
        'all_categories': all_categories
    }

    return render(request, 'met_explore/index.html', context)



def about(request):
    return render(request, 'met_explore/about.html')


def background(request):
    return render(request, 'met_explore/background.html')


def exp_protocols(request):
    return render(request, 'met_explore/exp_protocols.html')


def glossary(request):
    return render(request, 'met_explore/glossary.html')


def feedback(request):
    # add to the top

    # add to your views
    # def contact(request):
    #     form_class = ContactForm
    #
    #     return render(request, 'met_explore/feedback.html', {
    #         'form': form_class,
    #     })

    return render(request, 'met_explore/feedback.html')


def links(request):
    return render(request, 'met_explore/links.html')


def credits(request):
    return render(request, 'met_explore/credits.html')


def metabolite_data(request, cmpd_ids):
    """
    :param request: Request for the metabolite data for the Met Explorer all page
    :return: The cached url of the ajax data for the metabolite data table.
    """

    logger.info("Metabolite data requested")

    start = timeit.default_timer()

    if cmpd_ids == "All":

        compounds = Compound.objects.all().order_by('id')

    else:
        cmpd_list = cmpd_ids.split(',')
        logger.debug(cmpd_list)
        compounds = Compound.objects.filter(id__in=list(cmpd_list)).order_by('id')

    data_list = []
    for c in compounds:
        molecule_data = []
        metabolite = c.cmpd_name
        cmpd_id = c.id
        molecule_data.append(cmpd_id)
        molecule_data.append(metabolite)
        molecule_data.append(c.cmpd_formula)

        # Get the list of other names
        name_list = list(CompoundDBDetails.objects.filter(compound_id=cmpd_id).values_list('cmpd_name', flat=True))

        if metabolite in name_list:
            name_list = [x for x in name_list if x != metabolite]
            # If the names are the same as the metabolite name don't add as a synonym
        if name_list:
            name_list = list(dict.fromkeys(name_list))  # Don't add duplicate names
            name_string = ', '.join(name_list)
            molecule_data.append(name_string)
        else:
            molecule_data.append(None)

        id_list = list(CompoundDBDetails.objects.filter(compound_id=cmpd_id).values_list('identifier', flat=True))
        for i in id_list:
            if i.startswith('Std'):
                id_list.remove(i)

        chebi_id = c.chebi_id
        if chebi_id:
            chebi_id = "CHEBI:" + chebi_id
            id_list.insert(0, chebi_id)

        id_string = ', '.join(id_list)
        molecule_data.append(id_string)

        data_list.append(molecule_data)

    stop = timeit.default_timer()
    logger.info("Returning the metabolite data took: %s S" % str(stop - start))

    return JsonResponse({'data': data_list})


def metabolite_search(request, analysis_id):
    """
    View to return the metabolite search page
    :returns: Render met_explore/metabolite_search_tissue
    """
    # Min/Max values to send back to the view for colouring the table - these only change if the values from  the table are outwith this range.

    if request.method == 'GET':  # If the URL is loaded
        search_query = request.GET.get('metabolite_search', None)
        analysis = Analysis.objects.get(id=analysis_id)
        logger.debug('Found analysis_name = %s' % analysis.name)

        columns, met_table_data, min, max, mean, pathways, references, peak_id = get_metabolite_search_page(analysis, search_query)
        all_categories = get_search_categories(UI_CONFIG)
        uic = get_ui_config(UI_CONFIG, analysis_id)
        current_category = uic.category
        case_label = uic.case_label
        control_label = uic.control_label
        display_colnames = get_display_colnames(columns, uic.colnames)

        logger.debug("met_table_data %s" % met_table_data)
        logger.debug("columns %s" % columns)

        context = {
            'peak_id': peak_id,
            'columns': display_colnames,
            'metabolite': search_query,
            'analysis_id': analysis.id,
            'all_categories': all_categories,
            'current_category': current_category,
            'case_label': case_label,
            'control_label': control_label,
            'species': SPECIES,
            'met_table_data': met_table_data,
            'min': min,
            'max': max,
            'mean': mean,
            'pathways':pathways,
            'references': references,
            'json_url': reverse('get_metabolite_names')
        }

        logger.debug("The references are %s" % references)
        return render(request, 'met_explore/metabolite_search.html', context)


def pathway_search(request, analysis_id):
    """
    View to return the individual pathway search page
    :returns: Render met_explore/pathway_search

    """

    if request.method == 'GET':  # If the URL is loaded
        search_query = request.GET.get('pathway_search', None)
        analysis = Analysis.objects.get(id=analysis_id)

        pals_df, pals_min, pals_mean, pals_max = get_pals_view_data(analysis)
        pathway_id, summ_values, pwy_table_data = "", [], []

        # If we get a metabolite sent from the view
        current_category = None
        display_colnames = None
        case_label = None
        control_label = None
        if search_query is not None:
            pathway_id, summ_values, pwy_table_data, columns = get_pwy_search_table(pals_df, search_query, analysis)
            uic = get_ui_config(UI_CONFIG, analysis_id)
            current_category = uic.category
            case_label = uic.case_label
            control_label = uic.control_label
            display_colnames = get_display_colnames(columns, uic.colnames)

        reactome_token = get_highlight_token()
        # Get the indexes for M/z, RT and ID so that they are not formatted like the rest of the table

        all_categories = get_search_categories(UI_CONFIG)
        context = {
            'analysis_id': analysis_id,
            'all_categories': all_categories,
            'current_category': current_category,
            'columns': display_colnames,
            'case_label': case_label,
            'control_label': control_label,
            'species': SPECIES,
            'pwy_table_data': pwy_table_data,
            'pals_min': pals_min,
            'pals_max': pals_max,
            'pals_mean': pals_mean,
            'reactome_token': reactome_token,
            'pathway_name': search_query,
            'pathway_id': pathway_id,
            'summ_values': summ_values,
            'json_url': reverse('get_pathway_names')
        }

        return render(request, 'met_explore/pathway_search.html', context)


def get_pwy_search_table(pals_df, search_query, analysis):

    logger.info("getting %s table data" %search_query)

    pathway_id, summ_values, pwy_table_data = "", [], []
    pathway_id_names_dict = get_pathway_id_names_dict()

    try:
        pathway_id = pathway_id_names_dict[search_query]
        summ_table = pals_df[pals_df['Reactome ID'] == pathway_id][['PW F', 'DS F', 'F Cov']]
        summ_values_orig = summ_table.values.flatten().tolist()
        summ_values = [int(i) for i in summ_values_orig[:-1]]
        summ_values.append(summ_values_orig[-1])

        single_pwy_df = pals_df[pals_df['Reactome ID'] == pathway_id]

        primary_factor = get_factor_type_from_analysis(analysis, 'primary_factor')
        secondary_factor = get_factor_type_from_analysis(analysis, 'secondary_factor')

        analysis_case_factors = Factor.objects.filter(Q(group__case_group__analysis=analysis), Q(type=primary_factor))
        factor_names = set([a.name for a in analysis_case_factors if a.name != 'nan'])

        analysis_sec_factors = Factor.objects.filter(Q(group__case_group__analysis=analysis), Q(type=secondary_factor))
        columns = set([a.name for a in analysis_sec_factors if a.name != 'nan'])

        nm_samples_df = pd.DataFrame(index=factor_names, columns=columns, data="NM")  # Not measured samples

        for factor in factor_names:
            for ls in columns:
                try:
                    value = single_pwy_df.iloc[0][factor + ' (' + ls + ')']
                    nm_samples_df.loc[factor, ls] = value
                except KeyError as e:
                    pass

        pwy_values = nm_samples_df.values.tolist()  # This is what we are sending to the user.

        index = nm_samples_df.index.tolist()

        # Get a list to return to the view
        for t, v in zip(index, pwy_values):
            pwy_table_data.append(([t] + v))

    except KeyError:

        logger.warning("A pathway name %s was not passed to the search" % search_query)
        raise

    return pathway_id, summ_values, pwy_table_data, columns


def pathway_metabolites(request, analysis_id):
    """
    View to return the metabolite serach page
    :returns: Render met_explore/metabolite_search

    """
    if request.method == 'GET':  # If the URL is loaded
        search_query = request.GET.get('pathway_metabolites', None)
        met_peak_list, metabolite_names, cmpd_id_list, column_headers, summ_values = [], [], [], [], []
        min, max, mean = MIN, MAX, MEAN

        analysis = Analysis.objects.get(id=analysis_id)
        pals_df, _, _, _ = get_pals_view_data(analysis)

        # If we get a metabolite sent from the view
        if search_query is not None:

            pathway_id_names_dict = get_pathway_id_names_dict()

            try:
                pathway_id = pathway_id_names_dict[search_query]
                cmpd_id_list, metabolite_names, met_peak_list = pathway_search_data(pathway_id, analysis)
                view_df, min, mean, max = get_all_peaks_compare_df(analysis)

                sorted_view_df = sort_df_and_headers(view_df, analysis)
                column_headers = sorted_view_df.columns.tolist()

                # Here and send back the list of reactome compounds too...
                summ_table = pals_df[pals_df['Reactome ID'] == pathway_id][['PW F', 'DS F', 'F Cov']]
                summ_values_orig = summ_table.values.flatten().tolist()
                summ_values = [int(i) for i in summ_values_orig[:-1]]

                summ_values.append(summ_values_orig[-1])

            except KeyError:

                logger.warning("A pathway name %s was not passed to the search" % search_query)
                pass


        num_metabolites = len(metabolite_names)

        name_data = zip(cmpd_id_list, metabolite_names, met_peak_list)
        name_data_list = list(name_data)

        # Get the summary list for know/all metabolites in a pathway

        # Get the indexes for M/z, RT and ID so that they are not formatted like the rest of the table
        all_categories = get_search_categories(UI_CONFIG)
        uic = get_ui_config(UI_CONFIG, analysis_id)
        current_category = uic.category
        case_label = uic.case_label
        control_label = uic.control_label

        context = {
            'all_categories': all_categories,
            'analysis_id': analysis.pk,
            'current_category': current_category,
            'case_label': case_label,
            'control_label': control_label,
            'species': SPECIES,
            'cmpd_id_list': cmpd_id_list,
            'name_data': name_data_list,
            'metabolite_names': metabolite_names,
            'met_peak_list': met_peak_list,
            'num_metabolites': num_metabolites,
            'pathway_name': search_query,
            'columns': column_headers, 'max_value': max, 'min_value': min, 'mean_value': mean,
            'summ_values': summ_values,
            'json_url': reverse('get_pathway_names')
        }

        return render(request, 'met_explore/pathway_metabolites.html', context)


def met_ex_all(request, analysis_id, cmpd_list):
    """
    View to return the metabolite search page
    :returns: Render met_explore/metabolite_search
    """

    # TODO: set to 'peak_age_explorer' for the age data
    if analysis_id == 1:
        peak_url = 'peak_explorer/'
    elif analysis_id == 3:
        peak_url = 'peak_age_explorer/'
    else:
        peak_url = 'peak_explorer/'

    all_categories = get_search_categories(UI_CONFIG)
    uic = get_ui_config(UI_CONFIG, analysis_id)
    current_category = uic.category

    columns = ['cmpd_id', 'Metabolite', 'Formula', 'Synonyms', 'DB Identifiers']
    response = {
        'cmpd_list': cmpd_list,
        'columns': columns,
        'analysis_id': analysis_id,
        'peak_url': peak_url,
        'all_categories': all_categories,
        'current_category': current_category
    }

    return render(request, 'met_explore/met_ex_all.html', response)



def peak_ex_compare(request, peak_compare_list):
    """
       :param request: The peak Explorer page
       :param peak_list: The list of peaks required for the page
       :return: The template and required parameters for the peak explorer page.
       """

    analysis = Analysis.objects.get(name='Tissue Comparisons')

    if peak_compare_list == "All":
        peaks = Peak.objects.all()
    else:
        peak_list_split = peak_compare_list.split(',')
        peaks = Peak.objects.filter(id__in=list(peak_list_split))


    logger.info("Peak comparison table requested")
    start = timeit.default_timer()
    view_df, min, mean, max = get_peak_compare_df(analysis, peaks)

    sorted_view_df = sort_df_and_headers(view_df, analysis)
    column_headers = sorted_view_df.columns.tolist()

    stop = timeit.default_timer()


    logger.info("Returning the peak DF took: %s S" % str(stop - start))
    response = {'peak_compare_list': peak_compare_list, 'columns': column_headers, 'max_value': max, 'min_value': min,
                'mean_value': mean}

    return render(request, 'met_explore/peak_ex_compare.html', response)


def peak_age_compare(request, peak_compare_list):
    """
       :param request: The peak Explorer page
       :param peak_list: The list of peaks required for the page
       :return: The template and required parameters for the peak explorer page.
       """

    analysis = Analysis.objects.get(name='Age Comparisons')

    if peak_compare_list == "All":
        peaks = Peak.objects.all()
    else:
        peak_list_split = peak_compare_list.split(',')
        peaks = Peak.objects.filter(id__in=list(peak_list_split))

    logger.info("Peak comparison table requested")
    start = timeit.default_timer()
    view_df, min, mean, max = get_peak_compare_df(analysis, peaks)

    sorted_view_df = sort_df_and_headers(view_df, analysis)
    column_headers = sorted_view_df.columns.tolist()

    stop = timeit.default_timer()

    logger.info("Returning the peak DF took: %s S" % str(stop - start))
    response = {'peak_compare_list': peak_compare_list, 'columns': column_headers, 'max_value': max, 'min_value': min,
                'mean_value': mean}

    return render(request, 'met_explore/peak_age_compare.html', response)


def peak_mf_compare(request):
    """
       :param request: The peak Explorer page
       :return: The template and required parameters for the peak explorer page.
       """

    logger.info("Peak m/f comparison table requested")
    start = timeit.default_timer()

    analysis = Analysis.objects.get(name="M/F Comparisons")
    view_df, min, mean, max = get_peak_mf_compare_df(analysis)
    column_headers = get_peak_mf_header(view_df, analysis)


    stop = timeit.default_timer()

    logger.info("Returning the peak DF took: %s S" % str(stop - start))
    response = {'columns': column_headers, 'max_value': max, 'min_value': min,
                'mean_value': mean}

    return render(request, 'met_explore/peak_mf_compare.html', response)


def peak_mf_age_compare(request):
    """
       :param request: The peak Explorer page
       :return: The template and required parameters for the peak explorer page.
       """

    logger.info("Peak m/f age comparison table requested")
    start = timeit.default_timer()

    analysis = Analysis.objects.get(name="Age M/F Comparisons")
    view_df, min, mean, max = get_peak_mf_compare_df(analysis)

    column_headers = get_peak_mf_header(view_df, analysis)

    stop = timeit.default_timer()

    logger.info("Returning the peak DF took: %s S" % str(stop - start))
    response = {'columns': column_headers, 'max_value': max, 'min_value': min,
                'mean_value': mean}

    return render(request, 'met_explore/peak_mf_age_compare.html', response)



def peak_explorer(request, peak_list):
    """
    :param request: The peak Explorer page
    :return: The template and required parameters for the peak explorer page.
    """

    logger.debug("PEAK EXPLORER REQUEST for peaks %s" % peak_list)

    logger.info("Peak table requested")
    start = timeit.default_timer()

    analysis = Analysis.objects.get(name='Tissue Comparisons')
    peaks = Peak.objects.all()

    required_data = peaks.values('id', 'm_z', 'rt')

    peak_df = pd.DataFrame.from_records(list(required_data))
    peak_df[['m_z', 'rt']].round(3).astype(str)

    # Get all of the peaks and all of he intensities of the sample files
    # If we want all the colours to be for the whole table this should be cached?

    # group_df = cmpd_selector.get_group_df(peaks)

    ###KMCL Put this elsewhere to use for ALL_PEAKS GROUP DF.
    # cache.delete('my_group_df')
    if cache.get('my_group_df') is None:
        logger.debug("we dont have cache so running the function")
        cache.set('my_group_df', cmpd_selector.get_group_df(analysis, peaks), 60 * 18000)
        group_df = cache.get('my_group_df')
    else:
        logger.debug("we have cache so retrieving it")
        group_df = cache.get('my_group_df')

    max_value = np.nanmax(group_df)
    min_value = np.nanmin(group_df)
    mean_value = np.nanmean(group_df)
    group_df.reset_index(inplace=True)

    group_df.rename(columns={'peak': 'id'}, inplace=True)

    view_df = pd.merge(peak_df, group_df, on='id')

    sorted_df = sort_df_and_headers(view_df, analysis)
    column_headers = sorted_df.columns.tolist()

    stop = timeit.default_timer()

    logger.info("Returning the peak DF took: %s S" % str(stop - start))
    response = {'peak_list': peak_list, 'columns': column_headers, 'max_value': max_value, 'min_value': min_value,
                'mean_value': mean_value}

    return render(request, 'met_explore/peak_explorer.html', response)

def peak_age_explorer(request, peak_list):
    """
    :param request: The peak Explorer page
    :return: The template and required parameters for the peak explorer page.
    """
    analysis = Analysis.objects.get(name='Age Comparisons')

    logger.debug("PEAK EXPLORER REQUEST for peaks %s" % peak_list)

    logger.info("Peak table requested")
    start = timeit.default_timer()
    peaks = Peak.objects.all()

    required_data = peaks.values('id', 'm_z', 'rt')

    peak_df = pd.DataFrame.from_records(list(required_data))
    peak_df[['m_z', 'rt']].round(3).astype(str)

    # Get all of the peaks and all of he intensities of the sample files

    if cache.get('my_group_age_df') is None:
        logger.debug("we dont have cache so running the function")
        cache.set('my_group_age_df', cmpd_selector.get_group_df(analysis, peaks), 60 * 18000)
        group_df = cache.get('my_group_age_df')
    else:
        logger.debug("we have cache so retrieving it")
        group_df = cache.get('my_group_age_df')

    max_value = np.nanmax(group_df)
    min_value = np.nanmin(group_df)
    mean_value = np.nanmean(group_df)
    group_df.reset_index(inplace=True)

    group_df.rename(columns={'peak': 'id'}, inplace=True)
    view_df = pd.merge(peak_df, group_df, on='id')

    sorted_df = sort_df_and_headers(view_df, analysis)
    column_headers = sorted_df.columns.tolist()

    stop = timeit.default_timer()

    logger.info("Returning the peak DF took: %s S" % str(stop - start))
    response = {'peak_list': peak_list, 'columns': column_headers, 'max_value': max_value, 'min_value': min_value,
                'mean_value': mean_value}

    return render(request, 'met_explore/peak_age_explorer.html', response)


def get_all_peaks_compare_df(analysis):
    """
    A method to return the peak compare DF when all peaks are required and it is better to cache the result.
    :return: The peak_compare DF when all of the peaks are required. This is cached as it is used several times
    """

    peaks = Peak.objects.all()

    df_name = 'all_compare_df_'+str(analysis.id)

    if cache.get(df_name) is None:
        logger.debug("we dont have cache for %s so running the function" % df_name)
        cache.set(df_name, get_peak_compare_df(analysis, peaks), 60 * 18000)
        all_peak_compare_df, min_value, mean_value, max_value = cache.get(df_name)
    else:
        logger.debug("we have cache for %s so retrieving it" % df_name)
        all_peak_compare_df, min_value, mean_value, max_value = cache.get(df_name)

    return all_peak_compare_df, min_value, mean_value, max_value


def pals_data(request):
    """
    :param request: Request for the peak data for the Pathway explorer
    :return: The cached url of the ajax data for the pals data table.
    """
    analysis = Analysis.objects.get(name="Tissue Comparisons")
    view_df1, _, _, _ = get_pals_view_data(analysis)
    view_df = view_df1.fillna("-")
    #
    pals_data = view_df.values.tolist()

    logger.info("returning the pals data ")
    return JsonResponse({'data': pals_data})


def pals_age_data(request):
    """
    :param request: Request for the peak data for the Pathway explorer
    :return: The cached url of the ajax data for the pals data table.
    """
    analysis = Analysis.objects.get(name="Age Comparisons")
    view_df1, _, _, _ = get_pals_view_data(analysis)
    view_df = view_df1.fillna("-")
    #
    pals_data = view_df.values.tolist()

    logger.info("returning the pals data ")
    return JsonResponse({'data': pals_data})

def peak_compare_data(request, peak_compare_list):
    """
    :param request: Request for the peak data for the Peak Explorer page
    :return: The cached url of the ajax data for the peak data table.
    """
    analysis = Analysis.objects.get(name='Tissue Comparisons')

    if peak_compare_list == "All":

        peaks = Peak.objects.all()
    else:
        peak_compare_list = peak_compare_list.split(',')
        peaks = Peak.objects.filter(id__in=list(peak_compare_list))


    view_df1, _, _, _ = get_peak_compare_df(analysis, peaks)
    view_df_sorted = sort_df_and_headers(view_df1, analysis)
    view_df = view_df_sorted.fillna("-")

    #
    peak_compare_data = view_df.values.tolist()

    logger.info("returning the peak comparison data")
    return JsonResponse({'data': peak_compare_data})


def peak_mf_compare_data(request):
    """
    :param request: Request for the peak data for the Peak Explorer page
    :return: The cached url of the ajax data for the peak data table.
    """

    analysis = Analysis.objects.get(name="M/F Comparisons")

    view_df1, _, _, _ = get_peak_mf_compare_df(analysis)
    view_df_sorted = sort_df_and_headers(view_df1, analysis)
    view_df = view_df_sorted.fillna("-")
    #
    peak_compare_mf_data = view_df.values.tolist()

    logger.info("returning the peak comparison data")
    return JsonResponse({'data': peak_compare_mf_data})


def peak_age_compare_data(request, peak_compare_list):

    analysis = Analysis.objects.get(name='Age Comparisons')

    if peak_compare_list == "All":
        peaks = Peak.objects.all()

    else:
        peak_compare_list = peak_compare_list.split(',')
        peaks = Peak.objects.filter(id__in=list(peak_compare_list))

    view_df1, _, _, _ = get_peak_compare_df(analysis, peaks)

    view_df_sorted = sort_df_and_headers(view_df1, analysis)
    view_df = view_df_sorted.fillna("-")

    peak_age_compare_data = view_df.values.tolist()

    logger.info("returning the peak comparison data")
    return JsonResponse({'data': peak_age_compare_data})


def peak_mf_age_data(request):
    """
        :param request: Request for the peak data for the Peak Explorer page
        :return: The cached url of the ajax data for the peak data table.
        """
    analysis = Analysis.objects.get(name="Age M/F Comparisons")

    view_df1, _, _, _ = get_peak_mf_compare_df(analysis)
    view_df_sorted = sort_df_and_headers(view_df1, analysis)
    view_df = view_df_sorted.fillna("-")
    #
    peak_compare_mf_data = view_df.values.tolist()

    logger.info("returning the peak comparison data")
    return JsonResponse({'data': peak_compare_mf_data})


def peak_age_data(request, peak_list):
    """
    :param request: Request for the peak data for the Peak Explorer page
    :return: The cached url of the ajax data for the peak data table.
    """
    analysis = Analysis.objects.get(name='Age Comparisons')

    if peak_list == "All":
        peaks = Peak.objects.all()
    else:
        peak_list = peak_list.split(',')
        peaks = Peak.objects.filter(id__in=list(peak_list))

    required_data = peaks.values('id', 'm_z', 'rt')

    peak_df = pd.DataFrame.from_records(required_data)

    # # Get all of the peaks and all of the intensities of the sample files
    group_df = cmpd_selector.get_group_df(analysis, peaks)
    group_df.reset_index(inplace=True)
    group_df.rename(columns={'peak': 'id'}, inplace=True)

    view_df1 = pd.merge(peak_df, group_df, on='id')

    #Sort df to match headers
    view_df = sort_df_and_headers(view_df1, analysis)
    view_df = view_df.fillna("-")

    peak_data = view_df.values.tolist()

    logger.info("returning the peak data", peak_data)
    return JsonResponse({'data': peak_data})

def peak_data(request, peak_list):
    """
    :param request: Request for the peak data for the Peak Explorer page
    :return: The cached url of the ajax data for the peak data table.
    """
    analysis = Analysis.objects.get(name='Tissue Comparisons')

    if peak_list == "All":
        peaks = Peak.objects.all()

    else:
        peak_list = peak_list.split(',')
        peaks = Peak.objects.filter(id__in=list(peak_list))

    required_data = peaks.values('id', 'm_z', 'rt')
    peak_df = pd.DataFrame.from_records(required_data)

    # # Get all of the peaks and all of the intensities of the sample files
    group_df = cmpd_selector.get_group_df(analysis, peaks)

    group_df.reset_index(inplace=True)
    group_df.rename(columns={'peak': 'id'}, inplace=True)
    #
    view_df1 = pd.merge(peak_df, group_df, on='id')

    # Sort df to match headers
    view_df_sorted = sort_df_and_headers(view_df1, analysis)
    view_df = view_df_sorted.fillna("-")
    #
    peak_data = view_df.values.tolist()

    logger.info("returning the peak data")
    return JsonResponse({'data': peak_data})


def pathway_explorer(request):
    """
       :param request: The pathway Explorer page for the tissue data
       :return: The template and required parameters for the pathway explorer page.
       """
    analysis = Analysis.objects.get(name="Tissue Comparisons")
    logger.info("Pathway ranking table requested for analysis %s " % analysis)
    start = timeit.default_timer()
    view_df, pals_min, pals_mean, pals_max = get_pals_view_data(analysis)
    column_headers = view_df.columns.tolist()

    stop = timeit.default_timer()

    logger.info("Returning the pals data took: %s S" % str(stop - start))

    reactome_token = get_highlight_token()

    response = {'columns': column_headers, 'max_value': pals_max, 'min_value': pals_min,
                'mean_value': pals_mean, 'reactome_token': reactome_token}

    return render(request, 'met_explore/pathway_explorer.html', response)


def pathway_age_explorer(request):
    """
       :param request: The pathway Explorer page for the tissue data
       :return: The template and required parameters for the pathway explorer page.
       """

    analysis = Analysis.objects.get(name="Age Comparisons")
    logger.info("Pathway ranking table requested for analysis %s " % analysis)
    start = timeit.default_timer()
    view_df, pals_min, pals_mean, pals_max = get_pals_view_data(analysis)
    column_headers = view_df.columns.tolist()

    stop = timeit.default_timer()

    logger.info("Returning the pals data took: %s S" % str(stop - start))

    reactome_token = get_highlight_token()

    response = {'columns': column_headers, 'max_value': pals_max, 'min_value': pals_min,
                'mean_value': pals_mean, 'reactome_token': reactome_token}

    return render(request, 'met_explore/pathway_age_explorer.html', response)




def met_ex_tissues(request):
    """
    This view is equivalent to the met_age_id table.
        View to return the metabolite search page
        :returns: Render met_explore/met_ex_tissues and datatable

    """

    analysis = Analysis.objects.get(name="Tissue Comparisons")
    group_names = get_group_names(analysis)
    group_names.insert(0, "Metabolite")


    view_df = single_cmpds_df.drop(['cmpd_id'], axis=1, inplace=False)
    select_df = view_df[group_names]

    sorted_select_df = sort_df_and_headers(select_df, analysis)
    met_ex_list = sorted_select_df.values.tolist()

    column_headers = sorted_select_df.columns.tolist()

    # Get the max and mean values for the intensities to pass to the 'heat map'
    df2 = select_df.drop(['Metabolite'], axis=1, inplace=False)

    max_value = np.nanmax(df2)
    min_value = np.nanmin(df2)
    mean_value = np.nanmean(df2)

    response = {'columns': column_headers, 'data': met_ex_list, 'max_value': max_value, 'min_value': min_value,
                'mean_value': mean_value}

    return render(request, 'met_explore/met_ex_tissues.html', response)

def met_age_id(request):
    """
        View to return the metabolite search page
        :returns: Render met_explore/met_age_id and datatable
    """

    analysis = Analysis.objects.get(name="Age Comparisons")
    group_names = get_group_names(analysis)
    group_names.insert(0, "Metabolite")

    view_df = single_cmpds_df.drop(['cmpd_id'], axis=1, inplace=False)
    select_df = view_df[group_names]

    sorted_select_df = sort_df_and_headers(select_df, analysis)

    met_ex_list = sorted_select_df.values.tolist()
    column_headers = sorted_select_df.columns.tolist()

    # Get the max and mean values for the intensities to pass to the 'heat map'
    df2 = view_df.drop(['Metabolite'], axis=1, inplace=False)

    max_value = np.nanmax(df2)
    min_value = np.nanmin(df2)
    mean_value = np.nanmean(df2)

    response = {'columns': column_headers, 'data': met_ex_list, 'max_value': max_value, 'min_value': min_value,
                'mean_value': mean_value}

    return render(request, 'met_explore/met_age_id.html', response)


def get_metabolite_names(request):
    """
    A method to return a list of all the metabolite names present in the peaks
    :return: A unique list of peak compound names.
    """
    if request.is_ajax():

        metabolite_names = single_cmpds_df['Metabolite'].tolist()
        return JsonResponse({'metaboliteNames': metabolite_names})

    else:
        return JsonResponse({'metaboliteNames': ['Not', 'ajax']})


def get_pathway_names(request):
    """
       A method to return a list of all the Pathway names present in Reactome for the daea
       :return: A unique list of pathway names
    """

    analysis = Analysis.objects.get(name=UI_CONFIG[INITIAL_ANALYSIS])

    pals_df = get_cache_df(MIN_HITS, analysis)

    if request.is_ajax():
        pathway_names = pals_df.pw_name.tolist()
        return JsonResponse({'pathwayNames': pathway_names})

    else:
        return JsonResponse({'pathwayNames': ['Not', 'ajax']})


def pathway_search_data(pwy_id, analysis):
    """
    Given the pathway ID return the list of metabolites and associated peaks
    :param pwy_id: Reactome pathway ID
    :return: List of metabolite names followed by associated peaks in the pathway.
    """

    cmpd_form_dict = get_fly_pw_cmpd_formula(pwy_id)
    # peaks = Peak.objects.all()

    # analysis = Analysis.objects.get(name='Tissue Comparisons')

    peak_compare_df, _, _, _ = get_all_peaks_compare_df(analysis)
    peak_compare_df = peak_compare_df.fillna("-")

    met_name_list = []
    met_peak_list = []
    cmpd_id_list = []
    for cmpd, form in cmpd_form_dict.items():

        try:
            cmpd_name = Compound.objects.get(chebi_id=cmpd).cmpd_name
            cmpd_id = Compound.objects.get(chebi_id=cmpd).id
        except ObjectDoesNotExist:
            cmpd_name = Compound.objects.get(related_chebi__contains=cmpd).cmpd_name
            cmpd_id = Compound.objects.get(related_chebi__contains=cmpd).id
        except Exception as e:
            logger.warning("A compound for chebi id %s was not found, this shouldn't happen" % cmpd)
            logger.warning("Failed with the exception %s " % e)
            raise e

        met_name_list.append(cmpd_name)
        peaks = Peak.objects.filter(compound__id=cmpd_id)
        peak_list = [p.id for p in peaks]
        m_peaks = peak_compare_df[peak_compare_df['id'].isin(peak_list)]

        # Sort data to match sorted column headers
        m_peaks_sorted = sort_df_and_headers(m_peaks, analysis)

        m_peaks_data = m_peaks_sorted.values.tolist()
        met_peak_list.append(m_peaks_data)
        cmpd_id_list.append(cmpd_id)

    return cmpd_id_list, met_name_list, met_peak_list


def get_compounds_details(cmpds):
    """
    :param cmpds: A list of compounds that all for which the references are required
    :return: A dictionary of cmpd_id: all the compound parameters
    """
    compounds_details = {}

    for cmpd in cmpds:
        cmpd_id = Compound.objects.get(chebi_id=cmpd).id
        references = cmpd_selector.get_simple_compound_details(cmpd_id)
        compounds_details[cmpd_id] = references

    return compounds_details


def metabolite_peak_data(request, cmpd_id):
    """

    :param request:
    :param cmpd_id: The ID of the cmpd that we want to obtain the peak info for
    :return: A list of peak groups, the number of cmpds that peak annotates and a confidence value for the annotation
    """

    pg = PeakGroups(cmpd_id)

    peak_groups = pg.get_peak_groups()
    gp_df_list = []
    for group_df in peak_groups:

        group_df["no_adducts"] = pd.Series([], dtype=object)
        for index, row in group_df.iterrows():
            peak = Peak.objects.get(id=row.peak_id)
            annots = Annotation.objects.filter(peak=peak)
            row.no_annots = len(annots)
            group_df.loc[index, 'no_adducts'] = len(annots)

        gp_df_list.append(group_df.to_dict('r'))
        # columns = group_df.columns.tolist()
        columns = []

        columns_for_display = {'peak_id': "Peak ID", 'adduct': 'Ion', 'rt': "RT", 'nm': "Mass"}
        # This little function makes sure we keep the useful columns in the same order as required
        for c in group_df.columns:
            if c in columns_for_display:
                columns.append(columns_for_display[c])

        columns.insert(0, 'Conf')

    return JsonResponse({'peak_groups': gp_df_list, 'columns': columns})


def metabolite_pathway_data(request, pw_id):
    """

    :param request:
    :param pw_id: The pathway ID that for which the compounds and formulas are required for
    :return: cmpd_id: formula dictionary
    """

    pw_cmpd_for_dict = get_fly_pw_cmpd_formula(pw_id)
    cmpd_details = {}
    for cmpd, formula in pw_cmpd_for_dict.items():

        try:
            cmpd_id = Compound.objects.get(chebi_id=cmpd).id
        except ObjectDoesNotExist:
            cmpd_id = Compound.objects.filter(related_chebi__contains=cmpd)[0].id

        references = cmpd_selector.get_simple_compound_details(cmpd_id)
        logger.debug(references)
        cmpd_details[cmpd_id] = references

    return JsonResponse({'cmpd_details': cmpd_details})


def peak_explore_annotation_data(request, peak_id):
    """

    :param request:
    :param peak_id: The ID of the peak for which we want the annotation information
    :return: A list of compound names, adducts and confidence values for a given peak.
    """

    peak = Peak.objects.get(id=peak_id)

    annots = Annotation.objects.filter(peak=peak)
    cmpd_ids = Annotation.objects.filter(peak=peak).values_list('compound_id', flat=True)

    adducts = annots.values_list('adduct', flat=True).order_by('compound_id')
    neutral_mass = annots.values_list('neutral_mass', flat=True).order_by('compound_id')
    conf_fact = annots.values_list('confidence', flat=True).order_by('compound_id')

    cmpds = Compound.objects.filter(id__in=cmpd_ids).order_by('id')

    cmpd_names = [c.cmpd_name for c in cmpds]

    no_other_cmpds = len(cmpd_names) - 1

    compound_ids = list(cmpd_ids)

    return JsonResponse({'cmpd_ids': compound_ids, 'no_other_cmpds': no_other_cmpds, 'neutral_mass': list(neutral_mass),
                         'cmpd_names': cmpd_names, 'adducts': list(adducts), 'conf_fact': list(conf_fact)})


def met_search_highchart_data(request, analysis_id, tissue, metabolite):
    """
       A method to return a list of tissue/intensity values for a given cmpd.
       :return: A list of dictionaries for the metabolite/tissue highcharts.

    """
    cmpd_selector = CompoundSelector()
    hc_int_df_duplicates = cmpd_selector.get_hc_int_df()
    analysis = Analysis.objects.get(id=analysis_id)

    case_s = analysis.get_case_samples()
    control_s = analysis.get_control_samples()

    samples = case_s | control_s

    # Should only be looking at a single compound

    single_cmpd_indexed = s_cmpds_df.index.values
    hc_int_df = hc_int_df_duplicates.loc[single_cmpd_indexed]


    # group_ls_tissue_dict relates the group name to the tissue and the Life stage{'Mid_m': ['Midgut', 'M']}

    group_ls_tissue_dict = cmpd_selector.get_group_tissue_ls_dicts(analysis, samples)
    gp_intensities = cmpd_selector.get_gp_intensity(analysis, metabolite, tissue, single_cmpds_df)

    all_intensities,  met_series_data, gp_names  =[], [], []

    i=0
    for gp, v in gp_intensities.items():
            factors = group_ls_tissue_dict[gp]
            if len(factors) == 2:
                pfact = factors[0]
                sfact = factors[1]
                met_series_data.append({'name': pfact+" "+sfact, 'y': v, 'drilldown': str(i+1)})
                gp_name = pfact + " " + sfact
            elif len(factors) == 1:
                pfact = factors[0]
                met_series_data.append({'name': pfact, 'y': v, 'drilldown': str(i+1)})
                gp_name = pfact
            else:
                logger.warning('Unsupported number of factors')

            all_intensities.append(cmpd_selector.get_group_ints(metabolite, gp, hc_int_df))
            gp_names.append(gp_name)
            i += 1

    groups = list(gp_intensities.keys())
    drilldown_data = get_drilldown_data_structure(groups, analysis)

    df = pd.DataFrame({'ints': all_intensities})

    # Change the NaNs to empty lists []
    df.loc[df['ints'].isnull(), ['ints']] = df.loc[df['ints'].isnull(), 'ints'].apply(lambda x: [])
    int_data = df.ints.values.tolist()

    # Replace the None in the drilldown data with the data from all_intensities.
    for drill, intensity in zip(drilldown_data, int_data):
        if intensity:
            for d, i in zip(drill, intensity):
                if not math.isnan(i):  # Replace if the value is not a nan - otherwise leave as None
                    d[1] = i

    # Return the interquartile range, q25 and q75, as the error bars.
    error_bar_data = []
    for d in all_intensities:
        np_data = np.array(d)
        np_data = np_data[~np.isnan(np_data)]  # for error bar calcs Nans are removed.

        if np_data.any():
            q25, q75 = np.percentile(np_data, [25, 75])
            error_series = [q25, q75]
        else:
            error_series = None
        error_bar_data.append(error_series)

    #
    logger.debug("Passing the series data %s" % met_series_data)
    logger.debug("Passing the error bar data %s" % error_bar_data)
    logger.debug("Passing the drilldown data %s" % drilldown_data)

    peak_id = cmpd_selector.get_peak_id(metabolite, single_cmpds_df)

    cmpd_id = single_cmpds_df['cmpd_id'].loc[peak_id]

    cmpd_details = cmpd_selector.get_compound_details(peak_id, cmpd_id)
    frank_annots = json.loads(cmpd_details['frank_annots'])
    probability = None

    if frank_annots is not None:
        probability = round(float(frank_annots['probability']), 1)

    return JsonResponse({'group_names': gp_names, 'probability': probability, 'series_data': met_series_data, 'error_bar_data': error_bar_data,
                         'drilldown_data': drilldown_data})


def get_pals_view_data(analysis):
    """
    :return: The pals DF and the min, mean and max values for the datatable colouring.
    """

    pals_df = get_cache_df(MIN_HITS, analysis)
    fly_pals_df = change_pals_col_names(pals_df)

    # dropping colums not required for calculating the min. max and mean for the datatable.

    met_info_columns = ['Reactome ID', 'Pathway name', 'PW F', 'DS F', 'F Cov']
    p_values_df = fly_pals_df.drop(met_info_columns, axis=1)
    pals_max_value = np.nanmax(p_values_df)
    pals_min_value = np.nanmin(p_values_df)
    pals_mean_value = np.nanmean(p_values_df)

    # reorder the sample values of the dataframe for the view
    df_unordered = fly_pals_df[['Reactome ID', 'Pathway name', 'PW F', 'DS F', 'F Cov']]
    df_to_order = fly_pals_df.drop(['Reactome ID', 'Pathway name', 'PW F', 'DS F', 'F Cov'], axis=1)

    ordered_df = df_to_order.reindex(sorted(df_to_order.columns), axis=1)

    final_df = pd.concat([df_unordered, ordered_df], axis=1)

    return final_df, pals_min_value, pals_mean_value, pals_max_value


def change_pals_col_names(pals_df):
    """
    :param pals_df: A dataframe returned fromm the PALS package
    :return: The pals_df with columns removed and headings changed for use on the website
    """

    pals_df.reset_index(inplace=True)
    columns = pals_df.columns
    # Drop the columns that are not required for the FlyMet page.
    drop_list = ['sf', 'exp_F', 'Ex_Cov']
    for c in columns:
        if 'p-value' in c:
            drop_list.append(c)
    pals_df.drop(drop_list, axis=1, inplace=True)

    # Rename the columns that are left for use on the website
    pals_df.rename(columns={'index': 'Reactome ID', 'pw_name': 'Pathway name', 'unq_pw_F': 'PW F', 'tot_ds_F': 'DS F',
                            'F_coverage': 'F Cov'}, inplace=True)
    for c in columns:
        if "ChEBI" in c:
            c_new = c.replace("ChEBI", "")
        else:
            c_new = c
        if 'comb_p' in c:
            split_c = c_new.split('/')
            col_name = split_c[0].strip()
            pals_df.rename(columns={c: col_name}, inplace=True)

    return pals_df


def get_peak_mf_compare_df(analysis):

    peaks = Peak.objects.all()
    required_data = peaks.values('id', 'm_z', 'rt')
    peak_df = pd.DataFrame.from_records(required_data)

    cache_name = "peak_mf_df_"+str(analysis.id)

    if cache.get(cache_name) is None:
        logger.debug("we dont have cache so running the function")
        cache.set(cache_name, cmpd_selector.get_group_df(analysis, peaks), 60 * 18000)
        group_df = cache.get(cache_name)
    else:
        logger.debug("we have cache so retrieving %s " % cache_name)
        group_df = cache.get(cache_name)


    # Add an index so that we can export the peak as one of the values.
    group_df.reset_index(inplace=True)
    group_df.rename(columns={'peak': 'id'}, inplace=True)

    # Remove all larvae samples
    filter_columns = [col_name for col_name in group_df.columns if not col_name.endswith('l')]

    # male_female dataframe
    mf_df = group_df[filter_columns].copy()

    # divide by the whole fly amount for the sex/life-stage.
    for c in filter_columns:
        if c.endswith('f'):
            tissue = c.replace("_f", "")
            try:
                mf_df[c] = mf_df[c].div(mf_df[tissue + '_m'])
            except KeyError:
                # There is no male equivalent for this tissue so drop this from the column names
                mf_df = mf_df.drop(columns=c, axis=1)

    female_columns = [col_name for col_name in mf_df.columns if not col_name.endswith('m')]

    f_df = mf_df[female_columns].copy()
    drop_list = ['id']
    log_df, min_value, mean_value, max_value = get_log_df(f_df, drop_list)

    peak_compare_mf = pd.merge(peak_df, log_df, on='id')

    return peak_compare_mf, min_value, mean_value, max_value


def get_peak_compare_df(analysis, peaks):
    """
    Get the DF needed for the peak-tissue-compare page
    :return: peak_df, min, mean, max values needed for colouring the table.
    """
    analysis_comparison = AnalysisComparison.objects.filter(analysis=analysis)
    control_ids = analysis_comparison.values_list('control_group', flat=True).distinct()
    controls = list(Group.objects.filter(id__in=control_ids).values_list('name', flat=True).distinct())

    required_data = peaks.values('id', 'm_z', 'rt')
    peak_df = pd.DataFrame.from_records(required_data)

    # Get all of the peaks and all of the intensities of the sample files
    group_df = cmpd_selector.get_group_df(analysis, peaks)

    # Add a minimum value to the whole fly data. This is so that we don't flatten any of the tissue data if
    # the whole fly data is missing. i.e. if the whole fly is missing and we divide the tissue by NaN we get
    # NaN for the tissue when in reality there was a greater intensity for the tissue than the whole fly.

    group_df[controls] = group_df[controls].replace(np.nan, WF_MIN)

    # Add an index so that we can export the peak as one of the values.
    group_df.reset_index(inplace=True)
    group_df.rename(columns={'peak': 'id'}, inplace=True)

    column_names = group_df.columns

    # divide the cases by the controls
    for c in column_names:
        if c not in controls:
            try:
                control = get_control_from_case(c, analysis_comparison)
                group_df[c] = group_df[c].div(group_df[control])
            except ObjectDoesNotExist:
                logger.warning('%s is not a case so skipping this column' % c )
                pass

    drop_list = ['id']+controls

    # Calculate the log fold change values for the table.
    log_df, min_value, mean_value, max_value = get_log_df(group_df, drop_list)

    peak_compare_df = pd.merge(peak_df, log_df, on='id')
    peak_compare_df = peak_compare_df.drop(controls, axis=1)


    return peak_compare_df, min_value, mean_value, max_value


def get_drilldown_data_structure(groups, analysis):
    """
    A method to return the structure of the drilldown data structure
    :return: A list of lists containing the drilldown data structure - this may change depending on the number of
    whole fly replicates.
    """
    # Get number of samples in this group.

    secondary_factor_type = get_factor_type_from_analysis(analysis, 'secondary_factor')
    primary_factor_type = get_factor_type_from_analysis(analysis, 'primary_factor')
    drilldown_data = []

    for g in groups:

        if secondary_factor_type is not None: # both primary and secondary are present
            s = Factor.objects.get(type=secondary_factor_type, group__name=g).name
            p = Factor.objects.get(type=primary_factor_type, group__name=g).name[0]

            num_samples = len(Sample.objects.filter(group__name=g))

            fw_list = []
            for f in range(1, num_samples + 1):
                f_num = p+s + str(f) #Male Brain would be shown as BM etc
                f_sample = [f_num, None]
                fw_list.append(f_sample)

            drilldown_data.append(fw_list)

        else: # no secondary factor, only primary
            p = Factor.objects.get(type=primary_factor_type, group__name=g).name[0]
            num_samples = len(Sample.objects.filter(group__name=g))
            fw_list = []
            for f in range(1, num_samples + 1):
                f_num = p + str(f)  # Male Brain would be shown as BM etc
                f_sample = [f_num, None]
                fw_list.append(f_sample)

            drilldown_data.append(fw_list)

    # logger.debug("Returning drilldown_data structure as %s" % drilldown_data)

    return drilldown_data


def get_log_df(df, drop_list):
    """

    :param df: DF that you want the log df calculated from, contains only values and an id column
    :param drop_list: list of columns to be dropped from the final dataframe
    :return: log_df, min, mean, max values found in this df
    """
    # Exclude the ID column for the calculation and then add it back to merge the DFs

    temp_df = df['id']
    df = df.drop(['id'], axis=1)  # remove id column
    log_df = np.log2(df)
    log_df.insert(0, 'id', temp_df)  # put id column back

    calc_df = log_df.drop(drop_list, axis=1)

    max_value = np.nanmax(calc_df)
    min_value = np.nanmin(calc_df)
    mean_value = np.nanmean(calc_df)

    return log_df, min_value, mean_value, max_value

def get_column_headers(data_group_names, analysis):

    """
    A method to return the column headers for a datatable given a list of group and data names.
    :param g_names: Group names
    :param d_names: Data names e.g. peak, mz, rt
    :return: data headers and column headers in format used in web browser
    """
    group_headers = []
    data_headers= []

    group_names, data_names = cmpd_selector.get_list_view_column_names(data_group_names, analysis)

    for g in group_names:
        group_headers.append(group_names[g])

    for d in data_names:
        data_headers.append(data_names[d])

    return data_headers, group_headers

def get_metabolite_search_page(analysis, search_query):

    case_s = analysis.get_case_samples()
    control_s = analysis.get_control_samples()
    samples = case_s | control_s

    primary_factor_type = get_factor_type_from_analysis(analysis, 'primary_factor')
    secondary_factor_type = get_factor_type_from_analysis(analysis, 'secondary_factor')

    all_factors = get_factors_from_samples(samples, primary_factor_type)
    control_factors = get_factors_from_samples(control_s, primary_factor_type)

    assert len(control_factors) == 1, 'The number of control factors should be 1, please check'
    control = control_factors[0]

    peak_id = None
    met_table_data, columns = [], []
    min = MIN
    max = MAX
    mean = MEAN
    references = None
    pathways = {}

    # If we get a metabolite sent from the view
    if search_query is not None:

        met_search_df = single_cmpds_df[single_cmpds_df['Metabolite'] == search_query]

        # If there is a row in the DF matching the searched for metabolite
        if met_search_df.shape[0] == 1:

            peak_id = met_search_df.index.values[0]
            cmpd_id = met_search_df.cmpd_id.values[0]

            logger.info("Getting the details for %s " % search_query)

            # Get the metabolite/tissue comparison DF
            columns = get_factors_from_samples(control_s, secondary_factor_type)
            single_factor = False
            if len(columns) == 0:
                single_factor = True
                columns = [None]

            df = pd.DataFrame(index=all_factors, columns=columns, dtype=float)
            nm_samples_df = pd.DataFrame(index=all_factors, columns=columns, data="NM")  # Not measured samples
            gp_tissue_ls_dict = cmpd_selector.get_group_tissue_ls_dicts(analysis, samples)

            # Fill in the DF with Tissue/Life stages and intensities.
            for factor in all_factors:
                for ls in columns:
                    if ls is not None: # both primary and secondary factors are present
                        for g in gp_tissue_ls_dict:
                            if gp_tissue_ls_dict[g] == [factor, ls]:
                                value = met_search_df.iloc[0][g]
                                df.loc[factor, ls] = value
                                nm_samples_df.loc[factor, ls] = value

                    else: # single factor only
                        for g in gp_tissue_ls_dict:
                            if gp_tissue_ls_dict[g] == [factor]:
                                value = met_search_df.iloc[0][g]
                                df.loc[factor, ls] = value
                                nm_samples_df.loc[factor, ls] = value

            if single_factor: # get rid of None as the column header, replace with 'FC'
                columns = ['FC']
                df = df.rename(columns={None: columns[0]})
                nm_samples_df = nm_samples_df.rename(columns={None: columns[0]})

            # Standardise the DF by dividing by the Whole cell/Lifestage
            whole_row = df.loc[control]

            # Add a minimum value to the whole fly data. This is so that we don't flatten any of the tissue data if
            # the whole fly data is missing. i.e. if the whole fly is missing and we divide the tissue by NaN we get
            # NaN for the tissue when in reality there was a greater intensity for the tissue than the whole fly.
            whole_row = whole_row.replace(np.nan, WF_MIN)

            sdf = df.divide(whole_row)  # Standardised df - divided by the row with the whole data.
            log_df = np.log2(sdf)
            view_df = log_df.drop(index=control).round(2)

            nm_df = nm_samples_df.drop(index=control)
            nm2 = nm_df[nm_df == 'NM']

            log_nm_df = nm2.combine_first(view_df)  # Replace NM values for not measured samples in final df
            log_nm = log_nm_df.fillna("-")
            log_values = log_nm.values.tolist()  # This is what we are sending to the user.

            index = view_df.index.tolist()
            # Get a list to return to the view
            met_table_data = []

            for t, v in zip(index, log_values):
                met_table_data.append(([t] + v))

            actual_min = np.nanmin(view_df)
            actual_max = np.nanmax(view_df)
            actual_mean = np.nanmean(view_df)

            # If the max and min values are outwith the standard range
            if (actual_min < MIN) or (actual_max > MAX):
                min = actual_min
                max = actual_max
                mean = actual_mean

            # Here this no longer works a treat
            references = cmpd_selector.get_compound_details(peak_id, cmpd_id)
            # Get the pathways associated with this compound ID
            pathway_ids = get_cmpd_pwys(cmpd_id)

            # Get pathway names based on their IDS.
            pwy_name_id_dict = get_name_id_dict(analysis)

            if pathway_ids:
                pathways = {k: v for k, v in pwy_name_id_dict.items() if k in pathway_ids}

    return columns, met_table_data, min, max, mean, pathways, references, peak_id


def sort_df_and_headers(view_df, analysis):
    """
    A method to take in data for a view and return the sorted view and headers
    :param view_df: A df that needs view headers and to be sorted (column order) to match headers.
    :return: view_df: sorted view df and sorted view headers
    """
    column_names = view_df.columns.tolist()

    data_headers, group_headers = get_column_headers(column_names, analysis)

    if data_headers:
        all_column_headers = data_headers + group_headers
    else:
        all_column_headers = group_headers

    # Put the correct headers on the data and the reorganise as required
    view_df.columns = all_column_headers

    # Sort headers as required
    group_headers.sort(key=natural_keys)

    if data_headers:
        view_headers = data_headers + group_headers  # Data headers not has correct header format
    else:
        view_headers = group_headers

    # Sort the df to match the headers
    view_df = view_df[view_headers]

    return view_df

def get_peak_mf_header(view_df, analysis):
    """

    :param view_df: A dataframe with group
    :return: A list of view headers for the DF
    """

    sorted_view_df = sort_df_and_headers(view_df, analysis)
    column_heads = sorted_view_df.columns.tolist()

    column_headers = []
    for new_header in column_heads:
        if new_header.endswith('(F)'):
            new_header = new_header.replace('(F)', "(F/M)")
        column_headers.append(new_header)

    return column_headers

def enzyme_search(request):

    return render(request, 'met_explore/enzyme_search.html')
