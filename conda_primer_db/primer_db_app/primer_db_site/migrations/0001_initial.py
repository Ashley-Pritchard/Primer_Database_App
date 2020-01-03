# Generated by Django 2.2.6 on 2019-12-20 08:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Amplicon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amplicon_name', models.CharField(max_length=100)),
                ('exon', models.CharField(blank=True, max_length=20, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('genomic_location_start', models.IntegerField(blank=True, null=True)),
                ('genomic_location_end', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Analysis_Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('analysis_type', models.CharField(max_length=30)),
            ],
            options={
                'ordering': ['analysis_type'],
            },
        ),
        migrations.CreateModel(
            name='Gene',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gene_name', models.CharField(max_length=50)),
                ('chromosome', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Imported_By',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imported_by', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Primer_Set',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('primer_set', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Primer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.TextField(max_length=150)),
                ('location', models.CharField(blank=True, max_length=50, null=True)),
                ('direction', models.CharField(max_length=5)),
                ('alt_name', models.TextField(blank=True, max_length=255, null=True)),
                ('ngs_audit_number', models.IntegerField(blank=True, null=True)),
                ('date_imported', models.CharField(blank=True, max_length=20, null=True)),
                ('amplicon_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='primer_db_site.Amplicon')),
                ('imported_by_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='primer_db_site.Imported_By')),
            ],
        ),
        migrations.AddField(
            model_name='amplicon',
            name='analysis_type_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='primer_db_site.Analysis_Type'),
        ),
        migrations.AddField(
            model_name='amplicon',
            name='gene_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='primer_db_site.Gene'),
        ),
        migrations.AddField(
            model_name='amplicon',
            name='primer_set_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='primer_db_site.Primer_Set'),
        ),
    ]
