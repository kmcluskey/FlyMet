from rest_framework import serializers
from met_explore.models import Sample, Peak, SamplePeak


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = ('name','life_stage', 'group','tissue','mutant')


class PeakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Peak
        fields = ('psec_id','m_z', 'neutral_mass','rt','polarity','cmpd_name', 'cmpd_formula','cmpd_identifiers','identified','frank_anno','adduct', 'db')


class SamplePeakSerializer(serializers.ModelSerializer):
    class Meta:
        model = SamplePeak
        fields = ('peak', 'sample','intensity')

