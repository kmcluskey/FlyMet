from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.urls import reverse
from met_explore.forms import ContactForm
from django.core.paginator import Paginator
from web_omics.settings import CACHE_DURATION

from django.utils import timezone
from django.views.generic.list import ListView

from met_explore.compound_selection import *
from met_explore.models import Peak, SamplePeak, Sample, CompoundDBDetails, Compound
from met_explore.peak_groups import PeakGroups
from met_explore.pathway_analysis import *

from django.core.cache import cache, caches
from django.views.decorators.cache import cache_page
from decimal import *

import pandas as pd
import logging
import numpy as np
import json
import django
import math
import timeit

MIN = -7
MAX = 7
MEAN = 0

logger = logging.getLogger(__name__)

# If the Db exists and has been initialised:
try:
    cmpd_selector = CompoundSelector()
    #DFs for all the peaks
    # int_df = cmpd_selector.construct_cmpd_intensity_df()
    # peak_group_int_df =  cmpd_selector.get_group_df(int_df)

    #DF for the Highly confident peaks
    hc_int_df = cmpd_selector.get_hc_int_df()
    s_cmpds_df = cmpd_selector.get_single_cmpd_df(hc_int_df)
    single_cmpds_df = s_cmpds_df.reindex(sorted(s_cmpds_df.columns[1:]), axis =1)
    single_cmpds_df.insert(0, "Metabolite", s_cmpds_df['Metabolite'])

except django.db.utils.OperationalError as e:

    logger.warning("I'm catching this error %s ", e)

    logger.warning("DB not ready, start server again once populated")
    cmpd_selector = None

except FileNotFoundError as e:

    logger.error("Please reinitialise DB and make sure the file %s exists ", "/data/" + HC_INTENSITY_FILE_NAME + ".pkl")
    logger.info("Returning the DF as None")

    cmpd_selector = None

except Exception as e:
    logger.warning("I'm catching this error %s ", e)
    logger.warning("Hopefully just that the DB not ready, start server again once populated")
    raise e


def index(request):
    # return HttpResponse("Hello, world. You're at the met_explore index page.")

    context = {
        'json_url': reverse('get_metabolite_names')
    }

    return render(request, 'met_explore/index.html', context)


def temp_his_pw(request):
    """
    View to return the metabolite serach page
    :returns: Render met_explore/metabolite_search
    """

    return render(request, 'met_explore/temp_his_pw.html')


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

def metabolite_data(request):

    """
    :param request: Request for the metabolite data for the Met Explorer all page
    :return: The cached url of the ajax data for the metabolite data table.
    """

    print ("METABOLITE DATA REQUEST")

    logger.info("Metabolite data requested")

    start = timeit.default_timer()

    compounds = Compound.objects.all().order_by('id')

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
            name_list = name_list.remove(
                metabolite)  # If the names are the same as the metabolite name don't add as a synonym

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
    logger.info("Returning the metabolite data took: %s S", str(stop - start))

    return JsonResponse({'data':data_list})


def metabolite_search(request):
    """
    View to return the metabolite search page
    :returns: Render met_explore/metabolite_search
    """
    # Min/Max values to send back to the view for colouring the table - these only change if the values from  the table are outwith this range.

    if request.method == 'GET':  # If the URL is loaded
        search_query = request.GET.get('metabolite_search', None)
        samples = Sample.objects.all()
        tissues = list(set([s.tissue for s in samples])) #List of individual tissues.

        met_table_data=[]
        min = MIN
        max = MAX
        mean = MEAN
        references = None

        # If we get a metabolite sent from the view
        if search_query is not None:

            met_search_df = single_cmpds_df[single_cmpds_df['Metabolite'] == search_query]

            print (met_search_df)

            #If there is a row in the DF matching the searched for metabolite
            if met_search_df.shape[0] == 1:

                peak_id = met_search_df.index.values[0]
                cmpd_id = met_search_df.cmpd_id.values[0]

                print ("COMPOUND_ID ", cmpd_id)

                logger.info("Getting the details for %s ", search_query)

                #Get the metabolite/tissue comparison DF

                columns = ['F', 'M', 'L']
                df = pd.DataFrame(index=tissues, columns=columns, dtype=float)
                nm_samples_df = pd.DataFrame(index=tissues, columns=columns, data="NM") #Not measured samples
                gp_tissue_ls_dict=cmpd_selector.get_group_tissue_ls_dicts(samples)

                #Fill in the DF with Tissue/Life stages and intensities.
                for tissue in tissues:
                    for ls in columns:
                        for g in gp_tissue_ls_dict:
                            if gp_tissue_ls_dict[g] == [tissue, ls]:
                                value = met_search_df.iloc[0][g]
                                df.loc[tissue, ls] = value
                                nm_samples_df.loc[tissue, ls] = value

                print("NOT read samples", nm_samples_df)
                #Standardise the DF by dividing by the Whole cell/Lifestage
                whole_row = df.loc['Whole']
                sdf = df.divide(whole_row) #Standardised df - divided by the row with the whole data.
                log_df = np.log2(sdf)
                view_df = log_df.drop(index='Whole').round(2)

                nm_df = nm_samples_df.drop(index='Whole')

                nm2 = nm_df[nm_df == 'NM']
                log_nm_df = nm2.combine_first(view_df)#Replace NM values for not measured samples in final df

                print(log_nm_df)

                log_nm = log_nm_df.fillna("-")

                log_values = log_nm.values.tolist() #This is what we are sending to the user.

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

                #Here this no longer works a treat
                references = cmpd_selector.get_compound_details(peak_id, cmpd_id)

        print ("met_table_data", met_table_data)
        context = {
            'metabolite': search_query,
            'met_table_data': met_table_data,
            'min': min,
            'max': max,
            'mean': mean,
            'references': references,
            'json_url': reverse('get_metabolite_names')
            }

        print ("The references are ", references)
        return render(request, 'met_explore/metabolite_search.html', context)



def enzyme_search(request):
    """
    View to return the metabolite search page
    :returns: Render met_explore/metabolite_search
    """

    return render(request, 'met_explore/enzyme_search.html')

def tissue_search(request):
    """
    View to return the metabolite serach page
    :returns: Render met_explore/metabolite_search
    """

    return render(request, 'met_explore/tissue_search.html')


def pathway_search(request):
    """
    View to return the metabolite serach page
    :returns: Render met_explore/metabolite_search
    """

    return render(request, 'met_explore/pathway_search.html')


def met_ex_gconditions(request):
    """
    View to return the metabolite serach page
    :returns: Render met_explore/metabolite_search
    """

    return render(request, 'met_explore/met_ex_gconditions.html')

def met_ex_mutants(request):
    """
    View to return the metabolite serach page
    :returns: Render met_explore/metabolite_search
    """

    return render(request, 'met_explore/met_ex_mutants.html')


def met_ex_all(request):
    """
    View to return the metabolite serach page
    :returns: Render met_explore/metabolite_search
    """

    columns = ['cmpd_id','Metabolite', 'Formula', 'Synonyms', 'DB Identifiers']

    response = {'columns': columns}

    return render(request, 'met_explore/met_ex_all.html', response)

def peak_ex_compare(request):
    """
       :param request: The peak Explorer page
       :return: The template and required parameters for the peak explorer page.
       """

    logger.info("Peak comparison table requested")
    start = timeit.default_timer()
    view_df, min, mean, max = get_peak_compare_df()
    column_names = view_df.columns.tolist()

    group_names = cmpd_selector.get_list_view_column_names(column_names)

    column_headers = []
    for c in column_names:
        column_headers.append(group_names[c])

    # Get the indexes for M/z, RT and ID so that they are not formatted like the rest of the table

    stop = timeit.default_timer()

    logger.info("Returning the peak DF took: %s S", str(stop - start))
    response = {'columns': column_headers, 'max_value': max, 'min_value': min,
                'mean_value': mean}

    return render(request, 'met_explore/peak_ex_compare.html', response)


def peak_explorer(request, peak_list):

    """
    :param request: The peak Explorer page
    :return: The template and required parameters for the peak explorer page.
    """

    print ("PEAK EXPLORER REQUEST", peak_list)

    logger.info("Peak table requested")
    start = timeit.default_timer()
    peaks = Peak.objects.all()

    required_data = peaks.values('id', 'm_z', 'rt')

    # peak_ids = [p.id for p in peaks]

    peak_df = pd.DataFrame.from_records(list(required_data))

    peak_df[['m_z', 'rt']].round(3).astype(str)

    # Get all of the peaks and all of he intensities of the sample files
    # If we want all the colours to be for the whole table this should be cached?

    # group_df = cmpd_selector.get_group_df(peaks)

    if cache.get('my_group_df') is None:
        print ("we dont have cache so running the function")
        cache.set('my_group_df', cmpd_selector.get_group_df(peaks), 60*18000)
        group_df = cache.get('my_group_df')
    else:
        print ("we have cache so retrieving it")
        group_df = cache.get('my_group_df')

    max_value = np.nanmax(group_df)
    min_value = np.nanmin(group_df)
    mean_value = np.nanmean(group_df)
    group_df.reset_index(inplace=True)


    group_df.rename(columns={'peak':'id'}, inplace=True)

    view_df = pd.merge(peak_df, group_df, on='id')

    column_names = view_df.columns.tolist()

    group_names = cmpd_selector.get_list_view_column_names(column_names)

    column_headers = []
    for c in column_names:
        column_headers.append(group_names[c])


    # Get the indexes for M/z, RT and ID so that they are not formatted like the rest of the table

    print ("PEAK LIST ", peak_list)
    stop = timeit.default_timer()

    logger.info("Returning the peak DF took: %s S", str(stop - start))
    response = {'peak_list': peak_list, 'columns': column_headers, 'max_value': max_value, 'min_value': min_value,
                'mean_value': mean_value}


    return render(request, 'met_explore/peak_explorer.html', response)


def pals_data(request):

    """
    :param request: Request for the peak data for the Pathway explorer
    :return: The cached url of the ajax data for the pals data table.
    """

    view_df1, _, _, _ = get_pals_view_data()
    view_df = view_df1.fillna("-")
    #
    pals_data = view_df.values.tolist()

    logger.info("returning the pals data ")
    return JsonResponse({'data': pals_data})



def peak_compare_data(request):

    """
    :param request: Request for the peak data for the Peak Explorer page
    :return: The cached url of the ajax data for the peak data table.
    """

    view_df1, _, _, _ = get_peak_compare_df()
    view_df = view_df1.fillna("-")
    #
    peak_compare_data = view_df.values.tolist()

    logger.info("returning the peak comparison data ", peak_compare_data)
    return JsonResponse({'data': peak_compare_data})

def peak_data(request, peak_list):

    """
    :param request: Request for the peak data for the Peak Explorer page
    :return: The cached url of the ajax data for the peak data table.
    """

    if peak_list=="All":

        peaks = Peak.objects.all()

    else:
        peak_list = peak_list.split(',')
        peaks = Peak.objects.filter(id__in=list(peak_list))


    print("The peak list is ", peak_list)

    required_data = peaks.values('id', 'm_z', 'rt')

    peak_df = pd.DataFrame.from_records(required_data)

    # # Get all of the peaks and all of the intensities of the sample files
    group_df = cmpd_selector.get_group_df(peaks)


    group_df.reset_index(inplace=True)
    group_df.rename(columns={'peak':'id'}, inplace=True)
    #
    view_df1 = pd.merge(peak_df, group_df, on='id')
    view_df = view_df1.fillna("-")
    #
    peak_data = view_df.values.tolist()

    print ("returning peak data ", peak_data)
    return JsonResponse({'data':peak_data})

def path_ex_lifestages(request):

    return render(request, 'met_explore/path_ex_lifestages.html')


def pathway_explorer(request):

    """
       :param request: The pathway Explorer page for the tissue data
       :return: The template and required parameters for the pathway explorer page.
       """

    logger.info("Pathway ranking table requested")
    start = timeit.default_timer()
    view_df, pals_min, pals_mean, pals_max = get_pals_view_data()
    column_headers = view_df.columns.tolist()

    stop = timeit.default_timer()

    logger.info("Returning the pals data took: %s S", str(stop - start))
    response = {'columns': column_headers, 'max_value': pals_max, 'min_value': pals_min,
                'mean_value': pals_mean}


    return render(request, 'met_explore/pathway_explorer.html', response)


def met_ex_tissues(request):
    """
        View to return the metabolite search page
        :returns: Render met_explore/met_ex_tissues and datatable
    """

    view_df = single_cmpds_df.drop(['cmpd_id'], axis=1, inplace=False)

    print (view_df.head())
    met_ex_list = view_df.values.tolist()
    column_names = view_df.columns.tolist()

    group_names = cmpd_selector.get_list_view_column_names(column_names)

    column_headers = []
    for c in column_names:
        column_headers.append(group_names[c])

    # Get the max and mean values for the intensities to pass to the 'heat map'
    df2 = view_df.drop(['Metabolite'], axis=1, inplace=False)

    max_value = np.nanmax(df2)
    min_value = np.nanmin(df2)
    mean_value = np.nanmean(df2)

    ######## DO WE NEED TO RETURN THIS DATA SEPERATELY FROM THE HTML??
    response = {'columns': column_headers, 'data': met_ex_list, 'max_value':max_value, 'min_value':min_value, 'mean_value':mean_value}

    return render(request, 'met_explore/met_ex_tissues.html', response)

def get_metabolite_names(request):
    """
    A method to return a list of all the metabolite names present in the peaks
    :return: A unique list of peak compound names.
    """
    if request.is_ajax():

        metabolite_names = single_cmpds_df['Metabolite'].tolist()
        return JsonResponse({'metaboliteNames':metabolite_names})

    else:
        return JsonResponse({'metaboliteNames':['Not', 'ajax']})

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

        # group_df = pd.DataFrame(a)
        # print ("GPDF", group_df)
        group_df["no_adducts"] = pd.Series([], dtype=object)
        for index, row in group_df.iterrows():
            peak = Peak.objects.get(id=row.peak_id)
            annots = Annotation.objects.filter(peak=peak)
            row.no_annots = len(annots)
            group_df.loc[index, 'no_adducts'] = len(annots)

        gp_df_list.append(group_df.to_dict('r'))
        # columns = group_df.columns.tolist()
        columns = []

        columns_for_display = {'peak_id': "Peak ID", 'adduct': 'Ion', 'rt': "RT", 'nm':"Mass"}
        # This little function makes sure we keep the useful columns in the same order as required
        for c in  group_df.columns:
            if c in columns_for_display:
                columns.append(columns_for_display[c])

        columns.insert(0,'Conf')


    return JsonResponse({'peak_groups':gp_df_list,'columns':columns})


def metabolite_pathway_data(request, pw_id):
    """

    :param request:
    :param pw_id: The pathway ID that for which the compounds and formulas are required for
    :return: cmpd_id: formula dictionary
    """

    pw_cmpd_for_dict = get_fly_pw_cmpd_formula(pw_id)
    cmpds = []
    cmpd_details = {}
    for cmpd, formula in  pw_cmpd_for_dict.items():

        cmpd_id = Compound.objects.get(chebi_id=cmpd).id
        references = cmpd_selector.get_simple_compound_details(cmpd_id)
        print (references)
        cmpd_details[cmpd] = references


    return JsonResponse({'cmpd_details':cmpd_details})



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

    no_other_cmpds = len(cmpd_names)-1

    return JsonResponse({'no_other_cmpds':no_other_cmpds, 'neutral_mass': list(neutral_mass), 'cmpd_names': cmpd_names, 'adducts': list(adducts), 'conf_fact': list(conf_fact)})



def met_search_highchart_data(request, tissue, metabolite):
    """
       A method to return a list of tissue/intensity values for a given cmpd.
       :return: A list of dictionaries for the metabolite/tissue highcharts.

    """

    cmpd_selector = CompoundSelector()

    hc_int_df_duplicates = cmpd_selector.get_hc_int_df()

    #Should only be looking at a single compound

    single_cmpd_indexed = s_cmpds_df.index.values

    hc_int_df = hc_int_df_duplicates.loc[single_cmpd_indexed]



    # DFs for all the peaks
    # int_df = cmpd_selector.construct_cmpd_intensity_df()
    # peak_group_int_df =  cmpd_selector.get_group_df(int_df)

    # DF for the Highly confident peaks
    # relates the group name to the tissue and the Life stage{'Mid_m': ['Midgut', 'M']}

    samples = Sample.objects.all()
    group_ls_tissue_dict = cmpd_selector.get_group_tissue_ls_dicts(samples)

    met_series_data = [{'name': "Adult Female",'y': None,'drilldown': "1"},{'name': "Adult Male",'y': None,'drilldown': "2"},
        {'name': "Larvae",'y':None ,'drilldown': "3"}]

    all_intensities = np.empty((3, 4), dtype=float)
    all_intensities[:] = np.nan
    gp_intensities = cmpd_selector.get_gp_intensity(metabolite, tissue, single_cmpds_df)

    print ("This is the group intensites ", gp_intensities)

    # KMcL it might be better to pass these and check the correct data is matched - currently this is a reminder.
    # AF = data[0], AM = data[1], L = data[2]
    # Get all the intensities for Female, Male and Larvae from the gp_intensities to pass to the highcharts.
    # The group intensities just have the group name so have to work out the LS from this.
    for gp, v in gp_intensities.items():
        if math.isnan(v):
            v =  np.nan_to_num(v) #Can't pass NaN to JSON so return a zero to the highchart.
        if group_ls_tissue_dict[gp][1] == 'F':
            met_series_data[0]['y'] = v
            all_intensities[0] = cmpd_selector.get_group_ints(metabolite, gp, hc_int_df)

        elif group_ls_tissue_dict[gp][1] == 'M':
            met_series_data[1]['y'] = v
            all_intensities[1] = cmpd_selector.get_group_ints(metabolite, gp, hc_int_df)

        elif group_ls_tissue_dict[gp][1] == 'L':
            met_series_data[2]['y'] = v
            all_intensities[2] = cmpd_selector.get_group_ints(metabolite, gp, hc_int_df)

    logger.info("Passing the series data %s", met_series_data)
    logger.info("all intensities F, M and Larvae are %s", all_intensities)

    # Return all the intensities as drilldown data to highcharts
    # The all_intensities data is a list of lists as 4 replicates for the LS: F, M and L

    drilldown_data = [[["F1", None], ["F2", None], ["F3", None], ["F4", None]],
                      [["M1", None], ["M2", None], ["M3", None], ["M4", None]],
                      [["L1", None], ["L2", None], ["L3", None], ["L4", None]]]

    int_data = np.nan_to_num(all_intensities).tolist()

    #Replace the None in the drilldown data with the data from all_intensities.
    for drill, intensity in zip(drilldown_data, int_data):
        for d, i in zip(drill, intensity):
            d[1] = i


    # Return the interquartile range, q25 and q75, as the error bars.
    error_data = []

    all_ints = all_intensities[~np.isnan(all_intensities)]

    for d in all_intensities:
        d = d[~np.isnan(d)]   # for error bar calcs Nans are removed.
        if d.any():
            q25, q75 = np.percentile(d, [25, 75])
            error_series =[q25, q75]
        else:
            error_series = None
        error_data.append(error_series)

    #Replacing the NaNs with zeros for highchart.
    error_bar_data = (np.nan_to_num(error_data)).tolist()

    logger.info("Passing the series data %s", met_series_data)
    logger.info("Passing the error bar data %s", error_bar_data)
    logger.info("Passing the drilldown data %s", drilldown_data)

    peak_id = cmpd_selector.get_peak_id(metabolite, single_cmpds_df)

    cmpd_id = single_cmpds_df['cmpd_id'].loc[peak_id]

    cmpd_details = cmpd_selector.get_compound_details(peak_id, cmpd_id)
    frank_annots = json.loads(cmpd_details['frank_annots'])
    probability = None

    if frank_annots is not None:
        probability = round(float(frank_annots['probability']),1)

    return JsonResponse({'probability': probability, 'series_data': met_series_data, 'error_bar_data': error_bar_data, 'drilldown_data': drilldown_data})


def get_pals_view_data():
    """
    :return: The pals DF and the min, mean and max values for the databale colouring.
    """

    pals_df = get_cache_df()
    print (pals_df.loc['R-DME-1483101', 'tot_ds_F'])

    fly_pals_df = change_pals_col_names(pals_df)

    #dropping colums not required for calculating the min. max and mean for the datatable.

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

    # fly_pals_df = fly_pals_df.reindex(sorted(fly_pals_df.columns[2:]), axis=1)

    return final_df,  pals_min_value,  pals_mean_value,  pals_max_value


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
    pals_df.drop(drop_list, axis = 1, inplace=True)

    # Rename the columns that are left for use on the website
    pals_df.rename(columns={'index': 'Reactome ID','pw_name': 'Pathway name','unq_pw_F': 'PW F','tot_ds_F' : 'DS F','F_coverage': 'F Cov'}, inplace=True)
    for c in columns:
        if "ChEBI" in c:
            c_new = c.replace("ChEBI","")
        else: c_new = c
        if 'comb_p' in c:
            split_c = c_new.split('/')
            col_name = split_c[0]
            pals_df.rename(columns={c:col_name}, inplace=True)

    return pals_df

def get_peak_compare_df():
    peaks = Peak.objects.all()
    required_data = peaks.values('id', 'm_z', 'rt')
    peak_df = pd.DataFrame.from_records(required_data)

    # Get all of the peaks and all of the intensities of the sample files

    if cache.get('full_group_df') is None:
        print("we dont have cache so running the function")
        cache.set('full_group_df', cmpd_selector.get_group_df(peaks), 60 * 18000)
        group_df = cache.get('full_group_df')
    else:
        print("we have cache so retrieving it")
        group_df = cache.get('full_group_df')

    # group_df = cmpd_selector.get_group_df(peaks)

    # Calculate the log fold change values for the table.

    # Add an index so that we can export the peak as one of the values.
    group_df.reset_index(inplace=True)
    group_df.rename(columns={'peak': 'id'}, inplace=True)

    column_names = group_df.columns

    # divide by the whole fly amount for the sex/life-stage.
    for c in column_names:
        if c.endswith('f'):
            group_df[c] = group_df[c].div(group_df['Whole_f'])
        elif c.endswith('l'):
            group_df[c] = group_df[c].div(group_df['Whole_l'])
        elif c.endswith('m'):  # it starts with m
            group_df[c] = group_df[c].div(group_df['Whole_m'])

    # Exclude the ID column for the calculation and then add it back to merge the DFs
    temp_df = group_df['id']
    group_df = group_df.drop(['id'], axis=1)
    log_df = np.log2(group_df)
    log_df.insert(0, 'id', temp_df)

    calc_df = log_df.drop(['id', 'Whole_f', 'Whole_m', 'Whole_l'], axis=1)

    max_value = np.nanmax(calc_df)
    min_value = np.nanmin(calc_df)
    mean_value = np.nanmean(calc_df)

    peak_compare_df = pd.merge(peak_df, log_df, on='id')

    peak_compare_df = peak_compare_df.drop(['Whole_f', 'Whole_m', 'Whole_l'], axis=1)

    return peak_compare_df, min_value, mean_value, max_value

class MetaboliteListView(ListView):

    model = Peak
    template_name = 'met_explore/metabolite_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
