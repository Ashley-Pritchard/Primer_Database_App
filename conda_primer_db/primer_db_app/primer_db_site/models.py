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

#	def save(self, *args, **kwargs):
#		if not self.slug:
#			self.slug = slugify(self.title)
#		super(Post, self).save(*args, **kwargs)

	def __str__(self):
		return self.analysis_type

	class Meta:
		ordering = ['analysis_type']

		def __unicode__(self):
			return self.title

class Gene(models.Model):
	gene_name = models.CharField(max_length=50)
	chromosome = models.CharField(max_length=5)

class Primer_Set(models.Model):
	primer_set = models.CharField(max_length=10)

	def __str__(self):
		return self.primer_set

# class Imported_By(models.Model):
# 	def __str__(self):
# 		return(self.imported_by)
# 	imported_by = models.CharField(max_length=30)
# 	choice = [("current", "current"), ("ex", "ex")]
# 	status = models.CharField(max_length = 10, default = 'current', choices = choice)

class Amplicon(models.Model):

	def __str__(self):
		return self.amplicon_name
	amplicon_name = models.CharField(max_length=100)
	exon = models.CharField(max_length=20, null=True, blank=True)
	gene_id = models.ForeignKey(Gene, on_delete = models.SET_NULL, null=True, blank=True)
	analysis_type_id = models.ForeignKey(Analysis_Type, on_delete = models.SET_NULL, null=True, blank=True)
	primer_set_id = models.ForeignKey(Primer_Set, on_delete = models.SET_NULL, null=True, blank=True)

class Modification(models.Model):
	def __str__(self):
		return self.modification
	modification = models.CharField(max_length=20)

class Direction(models.Model):
	def __str__(self):
		return self.direction
	direction = models.CharField(max_length=10)


class Order_reason(models.Model):
	def __str__(self):
		return self.reason
	reason = models.CharField(max_length=30)

class Primer(models.Model):
	name = models.TextField(max_length=150)
	sequence = models.TextField(max_length=150)
	genomic_location_start = models.IntegerField(null=True, blank=True)
	genomic_location_end = models.IntegerField(null=True, blank=True)
	location = models.CharField(max_length=50, null=True, blank=True)
	#direction = models.CharField(max_length=5)
	new_direction = models.ForeignKey(Direction, on_delete=models.PROTECT)
	alt_name = models.TextField(max_length=255, null=True, blank=True)
	ngs_audit_number = models.IntegerField(null=True, blank=True)
	comments = models.CharField(max_length=1000, null=True, blank=True)
	imported_by_id = models.ForeignKey(User, limit_choices_to={"is_active":True}, on_delete=models.PROTECT, null=True, blank=True)
	date_imported = models.DateField(null=True, blank=True)
	amplicon_id = models.ForeignKey(Amplicon, on_delete = models.SET_NULL, null=True, blank=True)
	version = models.IntegerField(blank=True, default='1')
	#choice_1 = [("", ""), ("HEX", "HEX"), ("6FAM", "6FAM"), ("5FAM", "5FAM"), ("TAM", "TAM"), ("BIOTIN", "BIOTIN")]
	#modification = models.CharField(max_length=10, choices=choice_1, null=True, blank=True)
	#modification_5 = models.CharField(max_length=10, choices=choice_1, null=True, blank=True)
	new_modification = models.ForeignKey(Modification, on_delete = models.PROTECT, null=True, default=None, related_name="new_modification")
	new_modification_5 = models.ForeignKey(Modification, on_delete = models.PROTECT, null=True, default=None, related_name="new_modification_5")
	choice_2 = [("Stocked", "Stocked"), ("Ordered", "Ordered"), ("Order Placed", "Order Placed"), ("Recieved", "Recieved"), ("In Testing Sanger", "In Testing Sanger"), ("In Testing Non-Sanger", "In Testing Non-Sanger"), ("Failed Validation", "Failed Validation"), ("Archived", "Archived")]
	order_status = models.CharField(max_length=50, default='Stocked', choices=choice_2)
	reason_archived = models.CharField(max_length=1000, null=True, blank=True)
	date_archived = models.DateField(null=True, blank=True)
	archived_by_id = models.ForeignKey(User, limit_choices_to={"is_active":True}, related_name = 'archived_by', on_delete = models.PROTECT, null=True, blank=True)
	date_order_placed = models.DateField(null=True, blank=True)
	date_order_recieved = models.DateField(null=True, blank=True)
	date_testing_completed = models.DateField(null=True, blank=True)
	date_retesting_completed = models.DateField(null=True, blank=True)
	# choice_3 = [("",""), ("Repeat order", "Repeat order"), ("New gene / version", "New gene / version"), ("NGS confirmation", "NGS confirmation"), ("Scientist R&D", "Scientist - R&D"), ("Other", "Other")]
	# reason_ordered = models.CharField(max_length=100, default="", choices=choice_3)
	new_reason_ordered = models.ForeignKey(Order_reason, on_delete = models.PROTECT)
	choice_4 = [("", ""), ("GTAAAACGACGGCCAGT", "GTAAAACGACGGCCAGT"), ("CAGGAAACAGCTATGAC", "CAGGAAACAGCTATGAC")]
	m13_tag = models.CharField(max_length=20, default="", choices=choice_4, null=True, blank=True)
	worksheet_number = models.CharField(max_length=1000, null=True, blank=True)
