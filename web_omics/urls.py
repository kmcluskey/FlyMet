from django.conf import settings
from django.contrib import admin
from django.urls import include, path
import web_omics.views as views
from django.views.generic import RedirectView


handler503 = 'web_omics.views.handler503'


urlpatterns = [
    path('', RedirectView.as_view(pattern_name='met_explore_index')),
    path('met_explore/', include('met_explore.urls')),
    path('admin/', admin.site.urls),
    path('registration/', include('registration.urls')),

]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
