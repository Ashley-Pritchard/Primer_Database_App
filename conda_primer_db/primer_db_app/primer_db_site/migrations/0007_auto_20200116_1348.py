# Generated by Django 2.2.6 on 2020-01-16 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primer_db_site', '0006_auto_20200116_1229'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='amplicon',
            name='comments',
        ),
        migrations.RemoveField(
            model_name='amplicon',
            name='genomic_location_end',
        ),
        migrations.RemoveField(
            model_name='amplicon',
            name='genomic_location_start',
        ),
        migrations.AddField(
            model_name='primer',
            name='comments',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='primer',
            name='genomic_location_end',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='primer',
            name='genomic_location_start',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]