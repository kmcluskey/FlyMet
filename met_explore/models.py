from django.db import models
from django.utils import timezone


class Group(models.Model):
    """
    This is a model to store the name of the groups that collects triplicate samples and can be used for case/control
    studies.
    """
    name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        """
        Method to return a representation of the Sample
        """
        return "Group " + self.name


class Sample(models.Model):
    """
    Model class defining an instance of an experimental Sample including the tissue and life-stage from which it came
    """
    # Here the sample name is unique as this is important for processing FlyMet data
    name = models.CharField(max_length=250, unique=True, blank=False)
    sample_group = models.ForeignKey(Group, on_delete=models.CASCADE, default=None)

    def get_factor_value(self, name):
        values = Factor.objects.filter(sample=self, name=name).values_list('value', flat=True)
        value = values[0] if len(values) > 0 else None
        return value
    #
    # def get_sample_group(self):
    #     group = Group.objects.filter(sample=self).valuess_list('name', flat=True)
    #     print ("getting sample_group")
    #     return group


    @property
    def life_stage(self): # for flymet compatibility
        return self.get_factor_value('life_stage')

    @property
    def tissue(self): # for flymet compatibility
        return self.get_factor_value('tissue')

    @property
    def mutant(self): # for flymet compatibility
        return self.get_factor_value('mutant')

    @property
    def group(self): # for flymet compatibility
        group = self.sample_group.name
        return group

    def  __str__(self):
        """
        Method to return a representation of the Sample
        """

        return "Sample " + self.name


class Factor(models.Model):
    """
    Model class defining an experimental factor of a sample, e.g. tissue and life-stage from which it came
    """
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    name = models.CharField(max_length=250, blank=False, null=False)
    value = models.CharField(max_length=250, blank=False, null=False)

    def  __str__(self):
        return "Sample %s factor %s value %s " % (self.sample, self.name, self.value)

class Analysis(models.Model):

    """
    Model class representing a single Analysis
    """
    name = models.CharField(max_length=250, unique=True, blank=False)
    type = models.CharField(max_length=250, blank=False, null=False)

    def  __str__(self):
        """
        Method to return a representation of the Analysis
        """
        return "Analysis" + self.name



class AnalysisComparison(models.Model):

    name = models.CharField(max_length=250, unique=True, blank=False)
    case_group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='case_sample')
    control_group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='control_sample')
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE) #deleting the analysis deletes this comparison

    @property
    def case(self):
        return self.case_group.name

    @property
    def control(self):
        return self.control_group.name


    def  __str__(self):
        """
        Method to return a representation of the AnalysisComparison including the name of the compound
        :return: String:
        """
        return "Analysis Comparison " + str(self.name)



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

    cmpd_formula = models.CharField(max_length=100)
    pc_sec_id = models.IntegerField(unique=False) #The pimp compound secondary ID - it's unique in the populating df,
    chebi_id = models.CharField(null=True, max_length=30, unique=True)
    chebi_name = models.CharField(null=True, max_length=250)
    inchikey = models.CharField(null = True, max_length=27)
    smiles =  models.CharField(null=True, max_length=250)
    cas_code = models.CharField(null=True, max_length=30)
    peaks = models.ManyToManyField(Peak, through='Annotation')
    related_chebi = models.CharField(null=True, max_length=100) #Chebi IDs of acid/base conjugated or tautomers of the original chebi_id


    @property
    def cmpd_name(self):
        """

        :return: A cmpd_name - primarily the KEGG name, then HMDB and then any/the first name in the list of compounds.
        Values-list if used as some compounds have more than one kegg/HMDB ID - think some are historical codes and now point to the same compound
        """
        if self.chebi_name:
            cmpd_name = self.chebi_name
        elif CompoundDBDetails.objects.filter(compound=self, db_name__db_name='kegg').exists():
            cmpd_name = CompoundDBDetails.objects.filter(compound=self, db_name__db_name='kegg').values_list('cmpd_name',flat=True)[0]
        elif CompoundDBDetails.objects.filter(compound=self, db_name__db_name='hmdb').exists():
            cmpd_name = CompoundDBDetails.objects.filter(compound=self, db_name__db_name='hmdb').values_list('cmpd_name',flat=True)[0]
        else: #Just grab any name
            cmpd_name = CompoundDBDetails.objects.filter(compound=self).values_list('cmpd_name', flat=True)[0]

        return cmpd_name

    def  __str__(self):
        """
        Method to return a representation of the Compound name
        :return: String:
        """

        return "Compound " + str(self.id) +" "+self.cmpd_name

    # Currently this just returns one kegg_id even if there are more than one
    def get_kegg_id(self):

        kegg_id = None

        if CompoundDBDetails.objects.filter(compound=self, db_name__db_name='kegg').exists():
            kegg_id = CompoundDBDetails.objects.filter(compound=self, db_name__db_name='kegg').values_list('identifier', flat=True)[0]

        return kegg_id
    # Currently this just returns one hmbd_id even if there are more than one
    def get_hmdb_id(self):

        hmdb_id = None

        if CompoundDBDetails.objects.filter(compound=self, db_name__db_name='hmdb').exists():
            hmdb_id = CompoundDBDetails.objects.filter(compound=self, db_name__db_name='hmdb').values_list('identifier', flat=True)[0]

        return hmdb_id

    ## Returns a list of all the identifiers associated with a compound in dictionary format
    def get_all_identifiers(self):

        db_objects = CompoundDBDetails.objects.filter(compound=self)
        all_identifiers = {}

        ### Add identfiers including chebi and cas as long as they are not Nan or None
        for d in db_objects:
            if not (d.identifier == 'nan' or d.identifier == None):
                all_identifiers[d.db_name.db_name] =  d.identifier

        if (self.cas_code != 'nan'):
            all_identifiers['cas-code']=self.cas_code

        if (self.chebi_id !=None):
            all_identifiers['chebi_id']=self.chebi_id

        return all_identifiers





class DBNames(models.Model):
    db_name = models.CharField(unique=True, max_length=100)

    def __str__(self):

        return "This is the " + self.db_name + " DB"


class CompoundDBDetails(models.Model):

    db_name = models.ForeignKey(DBNames, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=100)
    cmpd_name = models.CharField(max_length=250)
    compound = models.ForeignKey(Compound, on_delete=models.CASCADE)

    class Meta:
        ordering = ['db_name']

    def __str__(self):
        return self.cmpd_name + " found in " + self.db_name.db_name




class Annotation(models.Model):

    identified = models.CharField(max_length=100)  # Should be set at True or False
    frank_anno = models.CharField(max_length=600, null=True) #Stored as JSON
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



class UniqueToken(models.Model):
    """
    Model class to store unique and often temporary tokens
    """
    name = models.CharField(max_length=250, unique=True, blank=False)
    description =  models.CharField(max_length=250, blank = True)
    token = models.CharField(max_length=100)
    datetime = models.DateTimeField(default=timezone.now)  # for token expiration

    def  __str__(self):
        """
        Method to return a representation of the Token
        """
        return "Token " + self.name +" token " + self.token




