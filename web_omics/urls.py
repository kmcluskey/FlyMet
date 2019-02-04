from django.conf import settings
from django.contrib import admin
from django.urls import include, path
import web_omics.views as views

urlpatterns = [
    path('', views.index, name='main_index'),
    path('met_explore/', include('met_explore.urls')),
    path('admin/', admin.site.urls),
    path('registration/', include('registration.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
