from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='met_explore_index'),
    path('tissue_metabolites', views.MetaboliteListView.as_view(), name='tissue_metabolites'),
    path('metabolite_search', views.metabolite_search, name='metabolite_search'),
    path('mutant_metabolites', views.mutant_metabolite_search, name='mutant_metabolites'),
    path('life_stage_metabolites', views.ls_metabolite_search, name='life_stage_metabolites'),
    path('met_ex_tissues', views.met_ex_tissues, name='met_ex_tissues'),


]
