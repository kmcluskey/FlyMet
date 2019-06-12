from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='met_explore_index'),
    path('tissue_metabolites', views.MetaboliteListView.as_view(), name='tissue_metabolites'),
    path('metabolite_search', views.metabolite_search, name='metabolite_search'),
    path('met_ex_tissues', views.met_ex_tissues, name='met_ex_tissues'),
    path('met_ex_lifestages', views.met_ex_lifestages, name='met_ex_lifestages'),
    path('met_ex_mutants', views.met_ex_mutants, name='met_ex_mutants'),
    path('met_ex_gconditions', views.met_ex_gconditions, name='met_ex_gconditions'),
    path('enzyme_search', views.enzyme_search, name='enzyme_search'),
    path('tissue_search', views.tissue_search, name='tissue_search'),
    path('pathway_search', views.pathway_search, name='pathway_search'),
    path('temp_his_pw', views.temp_his_pw, name='temp_his_pw'),
    path('background', views.background, name='background'),
    path('credits', views.credits, name='credits'),
    path('feedback', views.feedback, name='feedback'),
    path('links', views.links, name='links'),
    path('about', views.about, name='about'),
    path('path_ex_tissues', views.path_ex_tissues, name='path_ex_tissues'),
    path('path_ex_lifestages', views.path_ex_lifestages, name='path_ex_lifestages'),
    path('peak_explorer', views.peak_explorer, name='peak_explorer'),
    path('get_metabolite_names', views.get_metabolite_names, name='get_metabolite_names'),
    path('met_search_highchart_data/<str:tissue>/<str:metabolite>', views.met_search_highchart_data, name='met_search_highchart_data'),

]
