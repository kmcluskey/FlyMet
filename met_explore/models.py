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

    cmpd_name = models.CharField(max_length=600)  # At this stage just a name for the metabolite
    cmpd_formula = models.CharField(max_length=100)
    #KMCL: Currently if the list of identifiers matches another list we assume it's the same compound.
    cmpd_identifiers = models.CharField(max_length=600)  # Any identifiers we can associate with the peak stored as JSON
    peaks = models.ManyToManyField(Peak, through='Annotation')

    def  __str__(self):
        """
        Method to return a representation of the Compound name
        :return: String:
        """

        return "Compound " + str(self.id) +" "+self.cmpd_name

    def get_kegg_id(self):

        kegg_id = None
        id_list = json.loads(self.cmpd_identifiers)

        if id_list[0]:
            kegg_ids = [i for i in id_list if i.startswith('C00')]
            if kegg_ids:
                kegg_id = kegg_ids[0]

        return kegg_id

    def get_hmdb_id(self):

        hmdb_id = None

        id_list = json.loads(self.cmpd_identifiers)

        if id_list[0]:  # If there is an entry in the list.
            hmdb_ids = [i for i in id_list if i.startswith('HMDB')]

            if hmdb_ids:
                hmdb_id = hmdb_ids[0]

        return hmdb_id

class Annotation(models.Model):

    identified = models.CharField(max_length=100)  # Should be set at True or False
    frank_anno = models.CharField(max_length=600, null=True) #Stored as JSON
    db = models.CharField(max_length=20)
    adduct = models.CharField(max_length=100)
    confidence = models.IntegerField(blank=False, null=False, default=0) #Level of confidence 1 is the top, zero means not set.
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








