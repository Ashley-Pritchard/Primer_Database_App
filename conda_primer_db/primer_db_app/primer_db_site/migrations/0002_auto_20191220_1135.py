# Generated by Django 2.2.6 on 2019-12-20 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primer_db_site', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amplicon',
            name='comments',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
