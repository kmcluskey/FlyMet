from django.contrib import admin
from met_explore.models import *

admin.site.register(Peak)
admin.site.register(Sample)
admin.site.register(SamplePeak)
admin.site.register(Compound)
admin.site.register(Annotation)

# Register your models here.
