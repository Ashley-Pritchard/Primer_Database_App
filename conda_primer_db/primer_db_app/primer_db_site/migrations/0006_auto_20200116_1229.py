# Generated by Django 2.2.6 on 2020-01-16 12:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('primer_db_site', '0005_auto_20200114_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='primer',
            name='archived_by_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='related_secondary_imported_by', to='primer_db_site.Imported_By'),
        ),
        migrations.AddField(
            model_name='primer',
            name='date_archived',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='primer',
            name='reason_archived',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='primer',
            name='imported_by_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='related_primary_imported_by', to='primer_db_site.Imported_By'),
        ),
    ]