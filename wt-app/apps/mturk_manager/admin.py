from mturk_manager.models import HITItem
from django.contrib import admin

class HITItemAdmin(admin.ModelAdmin):
    list_display = ('hitid', 'creation_date', 'status',)
    search_fields = ('hitid', 'status',)

admin.site.register(HITItem, HITItemAdmin)
