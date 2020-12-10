# Generated by Django 3.1.3 on 2020-12-04 15:47

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Analysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, unique=True)),
                ('type', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identified', models.CharField(max_length=100)),
                ('frank_anno', models.CharField(max_length=600, null=True)),
                ('adduct', models.CharField(max_length=100)),
                ('confidence', models.IntegerField(default=0)),
                ('neutral_mass', models.DecimalField(decimal_places=10, max_digits=20)),
                ('annotation_group', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Compound',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cmpd_formula', models.CharField(max_length=100)),
                ('pc_sec_id', models.IntegerField()),
                ('chebi_id', models.CharField(max_length=30, null=True, unique=True)),
                ('chebi_name', models.CharField(max_length=250, null=True)),
                ('inchikey', models.CharField(max_length=27, null=True)),
                ('smiles', models.CharField(max_length=250, null=True)),
                ('cas_code', models.CharField(max_length=30, null=True)),
                ('related_chebi', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DBNames',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Peak',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('psec_id', models.IntegerField(unique=True)),
                ('m_z', models.DecimalField(decimal_places=10, max_digits=20)),
                ('rt', models.DecimalField(decimal_places=10, max_digits=20)),
                ('polarity', models.CharField(max_length=8)),
                ('preferred_annotation_reason', models.CharField(max_length=600)),
                ('preferred_annotation', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='preferred_annotation', to='met_explore.annotation')),
            ],
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, unique=True)),
                ('sample_group', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='met_explore.group')),
            ],
        ),
        migrations.CreateModel(
            name='UniqueToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, unique=True)),
                ('description', models.CharField(blank=True, max_length=250)),
                ('token', models.CharField(max_length=100)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='SamplePeak',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('intensity', models.FloatField(blank=True, null=True)),
                ('peak', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='met_explore.peak')),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='met_explore.sample')),
            ],
        ),
        migrations.CreateModel(
            name='Factor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('value', models.CharField(max_length=250)),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='met_explore.sample')),
            ],
        ),
        migrations.CreateModel(
            name='CompoundDBDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=100)),
                ('cmpd_name', models.CharField(max_length=250)),
                ('compound', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='met_explore.compound')),
                ('db_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='met_explore.dbnames')),
            ],
            options={
                'ordering': ['db_name'],
            },
        ),
        migrations.AddField(
            model_name='compound',
            name='peaks',
            field=models.ManyToManyField(through='met_explore.Annotation', to='met_explore.Peak'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='compound',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='met_explore.compound'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='peak',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='met_explore.peak'),
        ),
        migrations.CreateModel(
            name='AnalysisComparison',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, unique=True)),
                ('analysis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='met_explore.analysis')),
                ('case_sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='case_sample', to='met_explore.group')),
                ('control_sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='control_sample', to='met_explore.group')),
            ],
        ),
    ]
