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

logger = logging.getLogger(__name__)

single_cmpd_df = remove_dup_cmpds()

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

    return render(request, 'met_explore/metabolite_search.html')


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

    met_ex_list = single_cmpd_df.values.tolist()
    column_names = single_cmpd_df.columns.tolist()

    group_names = get_list_view_column_names(column_names)

    column_headers = []
    for c in column_names:
        column_headers.append(group_names[c])

    # Get the max and mean values for the intensities to pass to the 'heat map'
    df2 = single_cmpd_df.drop(['Metabolite'], axis=1)

    max_value = df2.values.max()
    min_value = df2.values.min()
    mean_value = df2.values.mean()


    ######## DO WE NEED TO RETURN THIS DATA SEPERATELY FROM THE HTML??

    response = {'columns': column_headers, 'data': met_ex_list, 'max_value':max_value, 'min_value':min_value, 'mean_value':mean_value}

    return render(request, 'met_explore/met_ex_tissues.html', response)

def get_metabolite_names(request):
    """
    A method to return a list of all the metabolite names present in the peaks
    :return: A unique list of peak compound names.
    """
    if request.is_ajax():

        metabolite_names = single_cmpd_df['Metabolite'].tolist()
        return JsonResponse({'metaboliteNames':metabolite_names})

    else:
        return JsonResponse({'metaboliteNames':['Not', 'ajax']})



class MetaboliteListView(ListView):

    model = Peak
    template_name = 'met_explore/metabolite_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
