from django.shortcuts import render
from django.http import HttpResponse

from django.utils import timezone
from django.views.generic.list import ListView

from met_explore.models import Peak, SamplePeak, Sample


def index(request):
    return HttpResponse("Hello, world. You're at the met_explore index page.")

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

class MetaboliteListView(ListView):

    model = Peak
    template_name = 'met_explore/metabolite_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
