from django.contrib import admin
from met_explore.models import *

admin.site.register(Peak)
admin.site.register(Sample)
admin.site.register(SamplePeak)
admin.site.register(Compound)
admin.site.register(Annotation)
admin.site.register(CompoundDBDetails)
admin.site.register(DBNames)
admin.site.register(Group)
admin.site.register(Factor)
admin.site.register(Analysis)
admin.site.register(AnalysisComparison)
admin.site.register(UniqueToken)

# Register your models here.
