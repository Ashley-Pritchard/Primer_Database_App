from django.contrib import admin
from primer_db_site.models import Primer
from primer_db_site.models import Amplicon, Analysis_Type, Gene, Primer_Set, Imported_By

#add access to the database via the admin page 

admin.site.register(Primer)
admin.site.register(Amplicon)
admin.site.register(Analysis_Type)
admin.site.register(Gene)
admin.site.register(Primer_Set)
admin.site.register(Imported_By)
