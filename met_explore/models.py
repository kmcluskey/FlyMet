from django.db import models
from django_extensions.db.fields.json import JSONField
import json


class Sample(models.Model):
    """
    Model class defining an instance of an experimental Sample including the tissue and life-stage from which it came
    """
    # Here the sample name is unique as this is important for processing FlyMet data
    name = models.CharField(max_length=250, unique=True, blank=False)
    life_stage = models.CharField(max_length=250, blank=False)
    tissue = models.CharField(max_length=250)
    group = models.CharField(max_length=250, blank=True, null=True)
    mutant = models.CharField(max_length=250, blank=True, null=True)

    def  __str__(self):
        """
        Method to return a representation of the Sample
        """

        return "Sample " + self.name

class Peak(models.Model):
    """
    Model class representing a basic peak including the compound as a simple string.
    One peak per secondary peak ID in PiMP
    """

    psec_id = models.IntegerField(unique=True) #The secondary peak ID from PiMP
    m_z = models.DecimalField(max_digits=20, decimal_places=10)
    rt = models.DecimalField(max_digits=20, decimal_places=10)
    polarity = models.CharField(max_length=8)
    preferred_annotation =  models.ForeignKey('Annotation', on_delete=models.SET_NULL, null=True, related_name='preferred_annotation')
    preferred_annotation_reason = models.CharField(max_length=600)


    def  __str__(self):
        """
        Method to return a representation of the SamplePeak including the name of the compound
        :return: String:
        """

        return "Peak" + str(self.id)+ " of m/z " + str(self.m_z)

class Compound(models.Model):

    # cmpd_name = models.CharField(max_length=600)  # At this stage just a general name for the metabolite
    cmpd_formula = models.CharField(max_length=100)
    pc_sec_id = models.IntegerField(unique=True) #The pimp compound secondary ID
    #KMCL: Currently if the list of identifiers matches another list we assume it's the same compound.
    # cmpd_identifiers = models.CharField(max_length=600)  # Any identifiers we can associate with the peak stored as JSON
    peaks = models.ManyToManyField(Peak, through='Annotation')
    inchikey = models.CharField(max_length=27, null=True, blank=True)

    @property
    def cmpd_name(self):
        """

        :return: A cmpd_name - primarily the KEGG name, then HMDB and then any/the first name in the list of compounds.
        """

        if CompoundDBDetails.objects.filter(compound=self, db_name='kegg').exists():
            cmpd_name = CompoundDBDetails.objects.get(compound=self, db_name='kegg').cmpd_name
        elif CompoundDBDetails.objects.filter(compound=self, db_name='hmdb').exists():
            cmpd_name = CompoundDBDetails.objects.get(compound=self, db_name='hmdb').cmpd_name
        else: #Just grab any name
            cmpd_name = CompoundDBDetails.objects.filter(compound=self).values_list('cmpd_name', flat=True)[0]

        return cmpd_name

    def  __str__(self):
        """
        Method to return a representation of the Compound name
        :return: String:
        """

        return "Compound " + str(self.id) +" "+self.cmpd_name

    def get_kegg_id(self):

        kegg_id = None

        if CompoundDBDetails.objects.filter(compound=self, db_name='kegg').exists():
            kegg_id = CompoundDBDetails.objects.get(compound=self, db_name='kegg').identifier

        return kegg_id

    def get_hmdb_id(self):

        hmdb_id = None

        if CompoundDBDetails.objects.filter(compound=self, db_name='hmdb').exists():
            hmdb_id = CompoundDBDetails.objects.get(compound=self, db_name='hmdb').identifier

        return hmdb_id

class CompoundDBDetails(models.Model):

    db_name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=100)
    cmpd_name = models.CharField(max_length=250)
    compound = models.ForeignKey(Compound, on_delete=models.CASCADE)

    class Meta:
        ordering = ['db_name']

    def __str__(self):
        return self.cmpd_name + "found in " + self.db_name



class Annotation(models.Model):

    identified = models.CharField(max_length=100)  # Should be set at True or False
    frank_anno = models.CharField(max_length=600, null=True) #Stored as JSON
    db = models.CharField(max_length=20)
    adduct = models.CharField(max_length=100)
    confidence = models.IntegerField(blank=False, null=False, default=0) #Level of confidence 6 is the top, zero means not set.
    compound = models.ForeignKey(Compound, on_delete=models.CASCADE)
    peak = models.ForeignKey(Peak, on_delete=models.CASCADE)
    neutral_mass = models.DecimalField(max_digits=20, decimal_places=10)
    annotation_group = models.IntegerField(null=True) #Group to store related peaks through annotations

    def __str__(self):
        """
        Method to return a representation of the Annotation ID and compound name
        :return: String:
        """

        return "Annotation of peak " + str(self.peak.id) + " and compound " + self.compound.cmpd_name




class SamplePeak(models.Model):

    peak = models.ForeignKey(Peak, on_delete=models.CASCADE)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    intensity = models.FloatField(null=True, blank=True)

    def  __str__(self):

        """
        Method to return a representation of the SamplePeak including the name of the compound
        :return: String:
        """

        return "Sample: " + self.sample.name + " Peak: " + str(self.peak.id)








