from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse


from django.utils import timezone
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from decimal import Decimal
from collections import OrderedDict

from met_explore.compound_selection import *
from met_explore.models import Peak, SamplePeak, Sample

import pandas as pd
import operator
import collections
import logging
import numpy as np

logger = logging.getLogger(__name__)

single_cmpds_df = get_single_cmpd_df()

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
        # If we get a metabolite sent from the view
        if search_query is not None:

            met_search_df = single_cmpds_df[single_cmpds_df['Metabolite'] == search_query]

            print ("SHAPE ", met_search_df.shape[0])

            #If there is a row in the DF matching the searched for metabolite
            if met_search_df.shape[0] == 1:

                logger.info("Getting the details for %s ", search_query)

                #Get the metabolite/tissue comparison DF

                columns = ['F', 'M', 'L']
                df = pd.DataFrame(index=tissues, columns=columns, dtype=float)
                gp_tissue_ls_dict=get_group_tissue_ls_dicts(samples)

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

    context = {
        'metabolite': search_query,
        'met_table_data': met_table_data,
        'min': min,
        'max': max,
        'mean': mean
        }

    return render(request, 'met_explore/metabolite_search.html', context)


def enzyme_search(request):
    """
    View to return the metabolite serach page
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

    group_names = get_list_view_column_names(column_names)

    column_headers = []
    for c in column_names:
        column_headers.append(group_names[c])

    # Get the max and mean values for the intensities to pass to the 'heat map'
    df2 = single_cmpds_df.drop(['Metabolite'], axis=1)

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


def get_group_tissue_ls_dicts(samples):
    # Given the name of the groups get dictionaries giving the lifestage and/or tissue type of the group.

    gp_tissue_ls_dict = {}

    groups = set([s.group for s in samples])

    # Get the first sample with of the given group and get the tissue type

    for gp in groups:
        group_attributes = samples.filter(group=gp)[0]
        gp_tissue_ls_dict[gp] = [group_attributes.tissue, group_attributes.life_stage]

    return gp_tissue_ls_dict



class MetaboliteListView(ListView):

    model = Peak
    template_name = 'met_explore/metabolite_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
