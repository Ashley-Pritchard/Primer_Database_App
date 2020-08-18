from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

#create the tables of the primer database 

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
	choice = [("current", "current"), ("ex", "ex")]
	status = models.CharField(max_length = 10, default = 'current', choices = choice)

class Amplicon(models.Model):
	amplicon_name = models.CharField(max_length=100)
	exon = models.CharField(max_length=20, null=True, blank=True)
	gene_id = models.ForeignKey(Gene, on_delete = models.SET_NULL, null=True, blank=True)
	analysis_type_id = models.ForeignKey(Analysis_Type, on_delete = models.SET_NULL, null=True, blank=True)
	primer_set_id = models.ForeignKey(Primer_Set, on_delete = models.SET_NULL, null=True, blank=True)

class Primer(models.Model):
	name = models.TextField(max_length=150)
	sequence = models.TextField(max_length=150)
	genomic_location_start = models.IntegerField(null=True, blank=True)
	genomic_location_end = models.IntegerField(null=True, blank=True)
	location = models.CharField(max_length=50, null=True, blank=True)
	direction = models.CharField(max_length=5)
	alt_name = models.TextField(max_length=255, null=True, blank=True)
	ngs_audit_number = models.IntegerField(null=True, blank=True)
	comments = models.CharField(max_length=1000, null=True, blank=True)
	imported_by_id = models.ForeignKey(Imported_By, on_delete = models.SET_NULL, null=True, blank=True)
	date_imported = models.CharField(max_length=20, null=True, blank=True)
	amplicon_id = models.ForeignKey(Amplicon, on_delete = models.SET_NULL, null=True, blank=True)
	version = models.IntegerField(blank=True, default='1')
	choice_1 = [("HEX", "HEX"), ("6FAM", "6FAM"), ("5FAM", "5FAM"), ("TAM", "TAM"), ("BIOTIN", "BIOTIN"), ("", "")]
	modification = models.CharField(max_length=10, default="", choices=choice_1, null=True, blank=True)
	modification_5 = models.CharField(max_length=10, default="", choices=choice_1, null=True, blank=True)
	choice_2 = [("Stocked", "Stocked"), ("Ordered", "Ordered"), ("Order Placed", "Order Placed"), ("Recieved", "Recieved"), ("In Testing Sanger", "In Testing Sanger"), ("In Testing Non-Sanger", "In Testing Non-Sanger"), ("Failed Validation", "Failed Validation"), ("Archived", "Archived")]
	order_status = models.CharField(max_length=50, default='Stocked', choices=choice_2)
	reason_archived = models.CharField(max_length=1000, null=True, blank=True)
	date_archived = models.CharField(max_length=20, null=True, blank=True)
	archived_by_id = models.ForeignKey(Imported_By, related_name = 'archived_by', on_delete = models.SET_NULL, null=True, blank=True)
	date_order_placed = models.CharField(max_length=20, null=True, blank=True)
	date_order_recieved = models.CharField(max_length=20, null=True, blank=True)
	date_testing_completed = models.CharField(max_length=20, null=True, blank=True)
	date_retesting_completed = models.CharField(max_length=20, null=True, blank=True)
	choice_3 = [("Repeat order", "Repeat order"), ("New gene / version", "New gene / version"), ("NGS confirmation", "NGS confirmation"), ("Scientist R&D", "Scientist - R&D"), ("Other", "Other"), ("None", "None")]
	reason_ordered = models.CharField(max_length=100, default='None', choices=choice_3)
	choice_4 = [("GTAAAACGACGGCCAGT", "GTAAAACGACGGCCAGT"), ("CAGGAAACAGCTATGAC", "CAGGAAACAGCTATGAC"), ("None", "None")]
	m13_tag = models.CharField(max_length=20, default="None", choices=choice_4)
	worksheet_number = models.CharField(max_length=1000, null=True, blank=True)
