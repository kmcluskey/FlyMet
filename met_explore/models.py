from django.db import models
from django.utils import timezone
from jsonfield import JSONField


class Project(models.Model):
    """
    A model to store the project - this can be related to several different Analyses
    """
    name = models.CharField(max_length=250, unique=True)
    description = models.CharField(max_length=500)
    metadata = JSONField()

    def __str__(self):
        return "Project" + self.name


class Category(models.Model):
    """
    This model allows a project to be split into different categories, some projects may only have one Category
    FlyMet currently has 2: Tissue and Ages all from the same metabolomics and genomics files.
    """
    name = models.CharField(max_length=250, unique=True)
    description = models.CharField(max_length=500)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return "Category " + self.name


class Group(models.Model):
    """
    This is a model to store the name of the groups that collects triplicate samples and can be used for case/control
    studies.
    """
    name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return "Group " + self.name


class Factor(models.Model):
    """
    Model class defining an individual experimental factor of a sample, e.g. tissue and life-stage from which it came
    """
    group = models.ForeignKey(Group, on_delete=models.CASCADE, default=None)
    type = models.CharField(max_length=250, blank=False, null=False)  # previously name
    name = models.CharField(max_length=250, blank=False, null=False)  # previously value

    def __str__(self):
        return "Factor type %s name %s " % (self.type, self.name)


class Sample(models.Model):
    """
    Model class defining an instance of an experimental Sample including the tissue and life-stage from which it came
    """
    # Here the sample name is unique as this is important for processing FlyMet data
    name = models.CharField(max_length=250, unique=True, blank=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, default=None)

    def get_factor_dict(self):
        """
        :return: Dict of Factor type: factor Name where the name of the Factor is not 'nan'
        """
        factor_dict = {}
        factors = Factor.objects.filter(group=self.group)
        for f in factors:
            if f.name != 'nan':
                factor_dict[f.type] = f.name

        return factor_dict

    def get_sample_group(self):
        group = Group.objects.filter(sample=self).values_list('name', flat=True)
        return group

    def __str__(self):
        return "Sample " + self.name


class Analysis(models.Model):
    """
    Model class representing a single Analysis
    """
    name = models.CharField(max_length=250, unique=True, blank=False)
    type = models.CharField(max_length=250, blank=False, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return "Analysis " + self.name

    def get_control_groups(self):
        control_groups = set(Group.objects.filter(control_group__in=AnalysisComparison.objects.filter(analysis=self)))
        return control_groups

    def get_case_groups(self):
        case_groups = set(Group.objects.filter(case_group__in=AnalysisComparison.objects.filter(analysis=self)))
        return case_groups

    def get_control_factors(self):
        control_groups = self.get_control_groups()
        factors = Factor.objects.filter(group__in=control_groups)
        return factors

    def get_case_factors(self):
        case_groups = self.get_case_groups()
        factors = Factor.objects.filter(group__in=case_groups)
        return factors

    def get_control_samples(self):
        control_groups = self.get_control_groups()
        control_samples = Sample.objects.filter(group__in=control_groups)
        return control_samples

    def get_case_samples(self):
        case_groups = self.get_case_groups()
        case_samples = Sample.objects.filter(group__in=case_groups)
        return case_samples


class AnalysisComparison(models.Model):
    name = models.CharField(max_length=250, blank=False)  # This can be duplicated for different analyses.
    case_group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='case_group')
    control_group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='control_group')
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)  # deleting the analysis deletes this comparison

    @property
    def case(self):
        return self.case_group.name

    @property
    def control(self):
        return self.control_group.name

    def __str__(self):
        return "Analysis Comparison " + str(self.name)


class Peak(models.Model):
    """
    Model class representing a basic peak including the compound as a simple string.
    One peak per secondary peak ID in PiMP
    """

    psec_id = models.IntegerField(unique=True)  # The secondary peak ID from PiMP
    m_z = models.DecimalField(max_digits=20, decimal_places=10)
    rt = models.DecimalField(max_digits=20, decimal_places=10)
    polarity = models.CharField(max_length=8)
    preferred_annotation = models.ForeignKey('Annotation', on_delete=models.SET_NULL, null=True,
                                             related_name='preferred_annotation')
    preferred_annotation_reason = models.CharField(max_length=600)

    def __str__(self):
        return "Peak" + str(self.id) + " of m/z " + str(self.m_z)


class Compound(models.Model):
    cmpd_formula = models.CharField(max_length=100)
    pc_sec_id = models.IntegerField(unique=False)  # The pimp compound secondary ID - it's unique in the populating df,
    chebi_id = models.CharField(null=True, max_length=30, unique=True)
    chebi_name = models.CharField(null=True, max_length=250)
    inchikey = models.CharField(null=True, max_length=27)
    smiles = models.CharField(null=True, max_length=250)
    cas_code = models.CharField(null=True, max_length=30)
    peaks = models.ManyToManyField(Peak, through='Annotation')

    # Chebi IDs of acid/base conjugated or tautomers of the original chebi_id
    related_chebi = models.CharField(null=True,
                                     max_length=100)

    @property
    def cmpd_name(self):
        """
        :return: A cmpd_name - primarily the KEGG name, then HMDB and then any/the first name in
        the list of compounds.
        Values-list if used as some compounds have more than one kegg/HMDB ID -
        think some are historical codes and now point to the same compound
        """
        if self.chebi_name:
            cmpd_name = self.chebi_name
        elif CompoundDBDetails.objects.filter(compound=self, db_name__db_name='kegg').exists():
            cmpd_name = \
                CompoundDBDetails.objects.filter(compound=self, db_name__db_name='kegg').values_list('cmpd_name',
                                                                                                     flat=True)[0]
        elif CompoundDBDetails.objects.filter(compound=self, db_name__db_name='hmdb').exists():
            cmpd_name = \
                CompoundDBDetails.objects.filter(compound=self, db_name__db_name='hmdb').values_list('cmpd_name',
                                                                                                     flat=True)[0]
        else:  # Just grab any name
            cmpd_name = CompoundDBDetails.objects.filter(compound=self).values_list('cmpd_name', flat=True)[0]

        return cmpd_name

    def __str__(self):
        return "Compound " + str(self.id) + " " + self.cmpd_name

    # Currently this just returns one kegg_id even if there are more than one
    def get_kegg_id(self):
        kegg_id = None
        if CompoundDBDetails.objects.filter(compound=self, db_name__db_name='kegg').exists():
            kegg_id = CompoundDBDetails.objects.filter(compound=self, db_name__db_name='kegg').values_list('identifier',
                                                                                                           flat=True)[0]
        return kegg_id

    # Currently this just returns one hmbd_id even if there are more than one
    def get_hmdb_id(self):
        hmdb_id = None
        if CompoundDBDetails.objects.filter(compound=self, db_name__db_name='hmdb').exists():
            hmdb_id = CompoundDBDetails.objects.filter(compound=self, db_name__db_name='hmdb').values_list('identifier',
                                                                                                           flat=True)[0]
        return hmdb_id

    ## Returns a list of all the identifiers associated with a compound in dictionary format
    def get_all_identifiers(self):
        db_objects = CompoundDBDetails.objects.filter(compound=self)
        all_identifiers = {}

        ### Add identfiers including chebi and cas as long as they are not Nan or None
        for d in db_objects:
            if not (d.identifier == 'nan' or d.identifier == None):
                all_identifiers[d.db_name.db_name] = d.identifier

        if (self.cas_code != 'nan'):
            all_identifiers['cas-code'] = self.cas_code

        if (self.chebi_id != None):
            all_identifiers['chebi_id'] = self.chebi_id

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
    frank_anno = models.CharField(max_length=600, null=True)  # Stored as JSON
    adduct = models.CharField(max_length=100)
    confidence = models.IntegerField(blank=False, null=False,
                                     default=0)  # Level of confidence 6 is the top, zero means not set.
    compound = models.ForeignKey(Compound, on_delete=models.CASCADE)
    peak = models.ForeignKey(Peak, on_delete=models.CASCADE)
    neutral_mass = models.DecimalField(max_digits=20, decimal_places=10)
    annotation_group = models.IntegerField(null=True)  # Group to store related peaks through annotations

    def __str__(self):
        return "Annotation of peak " + str(self.peak.id) + " and compound " + self.compound.cmpd_name


class SamplePeak(models.Model):
    peak = models.ForeignKey(Peak, on_delete=models.CASCADE)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    intensity = models.FloatField(null=True, blank=True)

    def __str__(self):
        return "Sample: " + self.sample.name + " Peak: " + str(self.peak.id)


class UniqueToken(models.Model):
    """
    Model class to store unique and often temporary tokens
    """
    name = models.CharField(max_length=250, unique=True, blank=False)
    description = models.CharField(max_length=250, blank=True)
    token = models.CharField(max_length=100)
    datetime = models.DateTimeField(default=timezone.now)  # for token expiration

    def __str__(self):
        return "Token " + self.name + " token " + self.token
