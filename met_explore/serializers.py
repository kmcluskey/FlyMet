from rest_framework import serializers
from met_explore.models import *


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = ('name','life_stage', 'group','tissue','mutant')


class PeakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Peak
        fields = ('psec_id','m_z', 'neutral_mass','rt','polarity')


class SamplePeakSerializer(serializers.ModelSerializer):
    class Meta:
        model = SamplePeak
        fields = ('peak', 'sample','intensity')


class CompoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compound
        fields = ('peak', 'cmpd_name', 'cmpd_formula','cmpd_identifiers')


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = ('peak', 'compound','identified','frank_anno','db', 'adduct')


