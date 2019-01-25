from django.shortcuts import render
from django.http import HttpResponse

from django.utils import timezone
from django.views.generic.list import ListView

from met_explore.models import Peak, SamplePeak, Sample

import pandas as pd
import operator
import collections

def index(request):
    # return HttpResponse("Hello, world. You're at the met_explore index page.")
    return render(request, 'index.html')

# Create your views here.

def metabolite_search(request):
    """
    View to return the metabolite serach page
    :returns: Render met_explore/metabolite_search
    """

    return render(request, 'met_explore/metabolite_search.html')

def mutant_metabolite_search(request):
    """
    View to return the metabolite serach page
    :returns: Render met_explore/metabolite_search
    """

    return render(request, 'met_explore/mutant_metabolites.html')

def ls_metabolite_search(request):
    """
    View to return the metabolite serach page
    :returns: Render met_explore/metabolite_search
    """

    return render(request, 'met_explore/life_stage_metabolites.html')

def met_ex_tissues(request):
    """
        View to return the metabolite serach page
        :returns: Render met_explore/metabolite_search and datatable
    """

    int_df = get_cmpd_intensity_df()
    group_df = get_group_df(int_df)

    peak_sids = list(int_df.index.values)
    compound_names = int_df['Metabolite'].tolist()
    group_df.insert(0, 'metabolite', compound_names)


    duplicate_compounds = [item for item, count in collections.Counter(compound_names).items() if count > 1]
    sec_ids_to_delete = []

    for dc in duplicate_compounds:
        dup_peaks = Peak.objects.filter(cmpd_name=dc)
        max_values_dict = {}
        for dp in dup_peaks:
            max_value = group_df.loc[dp.psec_id]['max_value']
            max_values_dict[dp.psec_id] = max_value
        print(max_values_dict)

        # Get the key with the maximum value to keep
        to_keep = max(max_values_dict.items(), key=operator.itemgetter(1))[0]
        keys = (list(max_values_dict.keys()))
        keys.remove(to_keep)
        print("we are removing these ", keys)
        for k in keys:
            sec_ids_to_delete.append(k)

    non_dup_ids = [sid for sid in peak_sids if sid not in sec_ids_to_delete]
    # Get a DF of cmpd_name, Group_columns and average values??
    met_ex_df = group_df.loc[non_dup_ids]

    return render(request, 'met_explore/met_ex_tissues.html')


# A df with all of the samples and their intensities for all of the peaks
# Index is peak sec ids and Metabolite column has the compound name.
def get_cmpd_intensity_df():

    samples = Sample.objects.all()
    peaks = Peak.objects.all()

    df_index = [p.psec_id for p in peaks]
    cmpds = [p.cmpd_name for p in peaks]
    columns = [s.name for s in samples]
    int_df = pd.DataFrame(index=df_index, columns=columns)

    for i in df_index:
        for c in columns:
            sp = SamplePeak.objects.get(peak__psec_id=i, sample__name=c)
            int_df.at[i, c] = sp.intensity

    int_df.insert(0, 'Metabolite', cmpds)

    return int_df


# This returns a DF with the groups/tissues and their average intensities and a maximum intensity for the row.
def get_group_df(int_df):

    samples = Sample.objects.all()
    sample_groups = set([sp.group for sp in samples])
    df_index = list(int_df.index.values)

    group_df = pd.DataFrame(index=df_index, columns=sample_groups)

    for group in sample_groups:
        print("sample_group ", group)
        gp_samples = Sample.objects.filter(group=group)
        int_list = []
        for i in df_index:
            for g in gp_samples:
                sample_name = g.name
                intensity = int_df.loc[i, sample_name]
                int_list.append(intensity)
            average_int = sum(int_list) / len(int_list)
            group_df.loc[i, group] = average_int

    group_df['max_value'] = group_df.max(axis=1)
    print ("yo")
    return group_df





class MetaboliteListView(ListView):

    model = Peak
    template_name = 'met_explore/metabolite_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
