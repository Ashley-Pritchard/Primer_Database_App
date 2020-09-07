from django.contrib import admin
from primer_db_site.models import Primer
from primer_db_site.models import Amplicon, Analysis_Type, Gene, Primer_Set, Modification

#Changes titles on Admin Site
admin.site.site_header="Primer Database Admin Page"
admin.site.index_title="PrimerDB Administration"
#Changes the "View site" URL
admin.site.site_url = "/primer_database/"

class GeneAdmin(admin.ModelAdmin):
	list_display = ('gene_name', 'chromosome')
	search_fields = ('gene_name', 'chromosome')

	def active(self, obj):
		return obj.is_active == 1

	active.boolean = True

# class Imported_ByAdmin(admin.ModelAdmin):
# 	list_display = ('imported_by', 'status')
# 	search_fields = ('imported_by', 'status')
#
# 	def active(self, obj):
# 		return obj.is_active == 1
#
# 	active.boolean = True

class AmpliconAdmin(admin.ModelAdmin):
	list_display = ('amplicon_name', 'exon')
	search_fields = ('amplicon_name', 'exon')

	def active(self, obj):
		return obj.is_active == 1

	active.boolean = True

class PrimerAdmin(admin.ModelAdmin):
	list_display = ('name', 'sequence', 'genomic_location_start', 'genomic_location_end', 'location',
					'direction', 'alt_name', 'ngs_audit_number', 'comments', 'date_imported', 'version',
					'm13_tag', 'prime_3_mod', 'prime_5_mod',  'order_status', 'date_order_placed', 'date_order_recieved',
					'date_testing_completed', 'reason_ordered', 'reason_archived', 'date_archived', 'worksheet_number')
	search_fields = ('name', 'location', 'direction', 'ngs_audit_number', 'new_modification', 'new_modification_5',
					'order_status', 'reason_ordered', 'reason_archived', 'm13_tag', 'worksheet_number')

	def active(self, obj):
		return obj.is_active == 1

	def prime_3_mod(self,obj):
		if obj.new_modification is not None:
			return obj.new_modification.modification
		else:
			return None
	def prime_5_mod(self,obj):
		if obj.new_modification_5 is not None:
			return obj.new_modification_5.modification
		else:
			return None
	prime_3_mod.short_description = "3' Modification"
	prime_3_mod.admin_order_field  = "new_modification"
	prime_5_mod.short_description = "5' Modification"
	prime_5_mod.admin_order_field  = "new_modification_5"
	active.boolean = True

#admin.site.register(Primer, PrimerAdmin, Analysis_Type, Analysis_TypeAdmin, Gene, GeneAdmin, Primer_Set, Primer_SetAdmin, Imported_By, Imported_ByAdmin, Amplicon, AmpliconAdmin)
admin.site.register(Analysis_Type)
admin.site.register(Gene, GeneAdmin)
admin.site.register(Primer_Set)
admin.site.register(Modification)
# admin.site.register(Imported_By, Imported_ByAdmin)
admin.site.register(Amplicon, AmpliconAdmin)
admin.site.register(Primer, PrimerAdmin)
