from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse


from django.utils import timezone
from django.views.generic.list import ListView
from django.views.generic import TemplateView

from met_explore.compound_selection import *
from met_explore.models import Peak, SamplePeak, Sample

import pandas as pd
import logging
import numpy as np

logger = logging.getLogger(__name__)

cmpd_selector = CompoundSelector()
single_cmpds_df = cmpd_selector.single_cmpds_df


def index(request):
    # return HttpResponse("Hello, world. You're at the met_explore index page.")
    return render(request, 'met_explore/index.html')

def temp_his_pw(request):
    """
    View to return the metabolite serach page
    :returns: Render met_explore/metabolite_search
    """

    return render(request, 'met_explore/temp_his_pw.html')


def about(request):
    return render(request, 'met_explore/about.html')

def importance(request):
    return render(request, 'met_explore/importance.html')

def feedback(request):
    return render(request, 'met_explore/feedback.html')

def links(request):
    return render(request, 'met_explore/links.html')

def metabolite_search(request):
    """
    View to return the metabolite serach page
    :returns: Render met_explore/metabolite_search
    """
    # Min/Max values to send back to the view for colouring the table - these only change if the values from  the table are outwith this range.

    MIN = -7
    MAX = 7
    MEAN = 0

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

            #If there is a row in the DF matching the searched for metabolite
            if met_search_df.shape[0] == 1:

                peak_id = met_search_df.index.values[0]

                logger.info("Getting the details for %s ", search_query)

                #Get the metabolite/tissue comparison DF

                columns = ['F', 'M', 'L']
                df = pd.DataFrame(index=tissues, columns=columns, dtype=float)
                gp_tissue_ls_dict=cmpd_selector.get_group_tissue_ls_dicts(samples)

                #Fill in the DF with Tissue/Life stages and intensities.
                for tissue in tissues:
                    for ls in columns:
                        for g in gp_tissue_ls_dict:
                            if gp_tissue_ls_dict[g] == [tissue, ls]:
                                value = met_search_df.iloc[0][g]
                                df.loc[tissue, ls] = value


                #Standardise the DF by dividing by the Whole cell/Lifestage
                standardised_df = df.div(df.loc['Whole'])
                log_df = np.log2(standardised_df)
                view_df = log_df.drop(index='Whole').round(2)
                log_values = view_df.values.tolist()
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

                references = cmpd_selector.get_compound_details(peak_id)

        context = {
            'metabolite': search_query,
            'met_table_data': met_table_data,
            'min': min,
            'max': max,
            'mean': mean,
            'references': references
            }

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


def met_ex_lifestages(request):
    """
    View to return the metabolite serach page
    :returns: Render met_explore/metabolite_search
    """

    return render(request, 'met_explore/met_ex_lifestages.html')

def peak_explorer(request):


    return render(request, 'met_explore/peak_explorer.html')


def path_ex_lifestages(request):

    return render(request, 'met_explore/path_ex_lifestages.html')


def path_ex_tissues(request):

    return render(request, 'met_explore/path_ex_tissues.html')


def met_ex_tissues(request):
    """
        View to return the metabolite search page
        :returns: Render met_explore/met_ex_tissues and datatable
    """

    met_ex_list = single_cmpds_df.values.tolist()
    print ("met_ex_list", met_ex_list)
    column_names = single_cmpds_df.columns.tolist()

    group_names = cmpd_selector.get_list_view_column_names(column_names)

    column_headers = []
    for c in column_names:
        column_headers.append(group_names[c])

    # Get the max and mean values for the intensities to pass to the 'heat map'
    df2 = single_cmpds_df.drop(['Metabolite'], axis=1, inplace=False)

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

def met_search_highchart_data(request, tissue):
    """
       A method to return a list of tissue/intensity values for a given cmpd.
       :return: A list of dictionaries for the metabolite/tissue highcharts.

    """
    group_ls_tissue_dict = cmpd_selector.group_ls_tissue_dict

    met_series_data = [{'name': "Adult Female",'y': None,'drilldown': "1"},{'name': "Adult Male",'y': None,'drilldown': "2"},
        {'name': "Larvae",'y':None ,'drilldown': "3"}]


    all_intensities = np.empty((3, 4))
    all_intensities[:] = np.nan
    # if request.is_ajax():
    # metabolite = request.GET['metabolite_search']
    metabolite = 'Histidine'
    tissue = tissue

    gp_intensities = cmpd_selector.get_gp_intensity(metabolite, tissue)
    print(gp_intensities)

    # AF = data[0]
    # AM = data[1]
    # L = data[2]

    for gp, v in gp_intensities.items():
        print(gp, v)
        if group_ls_tissue_dict[gp][1] == 'F':
            met_series_data[0]['y'] = v
            print (cmpd_selector.get_group_ints(metabolite, gp))
            all_intensities[0] = cmpd_selector.get_group_ints(metabolite, gp)
            print("This is the female intensity")

        elif group_ls_tissue_dict[gp][1] == 'M':
            print("This is the male intensity")
            met_series_data[1]['y'] = v
            print (cmpd_selector.get_group_ints(metabolite, gp))

            all_intensities[1] = cmpd_selector.get_group_ints(metabolite, gp)

        elif group_ls_tissue_dict[gp][1] == 'L':
            print("This is the larvae intensity")
            met_series_data[2]['y'] = v
            all_intensities[2] = cmpd_selector.get_group_ints(metabolite, gp)

    print("series data", met_series_data)
    print("all intensities for sample set", all_intensities)

    # Return the interquartile range - q25 and q75 as the error bars.
    error_data = []
    # all_intensities = np.array()
    for d in all_intensities:

        q25, q75 = np.percentile(d, [25, 75])
        error_series =[q25, q75]
        error_data.append(error_series)


    #Replacing the NaNs with zeros for highchart.
    error_bar_data= (np.nan_to_num(error_data)).tolist()

    print ("error_bar_data", error_bar_data)


    return JsonResponse({'series_data': met_series_data, 'error_bar_data': error_bar_data})

    # else:
    #
    #     pass


class MetaboliteListView(ListView):

    model = Peak
    template_name = 'met_explore/metabolite_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
