from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

#generate the primer database 

class Analysis_Type(models.Model):
	analysis_type = models.CharField(max_length=30)

	def get_absolute_url(self):
		return ('analysis_type', (),
			{
				'slug': self.slug,
			})

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.title)
		super(Post, self).save(*args, **kwargs)

	class Meta:
		ordering = ['analysis_type']

		def __unicode__(self):
			return self.title

class Gene(models.Model):
	gene_name = models.CharField(max_length=50)
	chromosome = models.CharField(max_length=5)

class Primer_Set(models.Model):
	primer_set = models.CharField(max_length=10)

class Imported_By(models.Model):
	imported_by = models.CharField(max_length=30)

class Amplicon(models.Model):
	amplicon_name = models.CharField(max_length=100)
	exon = models.CharField(max_length=20, null=True, blank=True)
	gene_id = models.ForeignKey(Gene, on_delete = models.SET_NULL, null=True, blank=True)
	analysis_type_id = models.ForeignKey(Analysis_Type, on_delete = models.SET_NULL, null=True, blank=True)
	primer_set_id = models.ForeignKey(Primer_Set, on_delete = models.SET_NULL, null=True, blank=True)

class Primer(models.Model):
	sequence = models.TextField(max_length=150)
	genomic_location_start = models.IntegerField(null=True, blank=True)
	genomic_location_end = models.IntegerField(null=True, blank=True)
	location = models.CharField(max_length=50, null=True, blank=True)
	direction = models.CharField(max_length=5)
	alt_name = models.TextField(max_length=255, null=True, blank=True)
	ngs_audit_number = models.IntegerField(null=True, blank=True)
	comments = models.CharField(max_length=1000, null=True, blank=True)
	imported_by_id = models.ForeignKey(Imported_By, related_name='related_primary_imported_by', on_delete = models.SET_NULL, null=True, blank=True)
	date_imported = models.CharField(max_length=20, null=True, blank=True)
	amplicon_id = models.ForeignKey(Amplicon, on_delete = models.SET_NULL, null=True, blank=True)
	version = models.IntegerField(blank=True, default='1')
	choice = [("Stocked", "Stocked"), ("Ordered", "Ordered"), ("Order Placed", "Order Placed"), ("Recieved", "Recieved"), ("In Testing", "In Testing"), ("Failed Validation", "Failed Validation"), ("Archived", "Archived")]
	order_status = models.CharField(max_length=50, default='Stocked', choices=choice)
	reason_archived = models.CharField(max_length=1000, null=True, blank=True)
	date_archived = models.CharField(max_length=20, null=True, blank=True)
	archived_by_id = models.ForeignKey(Imported_By, related_name='related_secondary_imported_by', on_delete = models.SET_NULL, null=True, blank=True)
	date_order_placed = models.CharField(max_length=20, null=True, blank=True)
	date_order_recieved = models.CharField(max_length=20, null=True, blank=True)
	date_testing_completed = models.CharField(max_length=20, null=True, blank=True)



