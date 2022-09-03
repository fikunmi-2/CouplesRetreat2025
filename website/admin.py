from django.contrib import admin
from .models import Registered
from import_export.admin import ImportExportModelAdmin


# admin.site.register(Registered)

@admin.register(Registered)
class Register_usersdata(ImportExportModelAdmin, admin.ModelAdmin):
	pass
	list_display = ('s_name', 'f_name_m', 'f_name_f',)
	search_fields = ('s_name',)
