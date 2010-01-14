from mturk_manager.models import HITConfig, HITItem
from django.contrib import admin

class HITConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'reward', 'bonus',)
    search_fields = ('name', 'title', 'description', 'reward', 'bonus',)

class HITItemAdmin(admin.ModelAdmin):
    list_display = ('hitid', 'creation_date', 'status',)
    search_fields = ('hitid', 'status',)

admin.site.register(HITConfig, HITConfigAdmin)    
admin.site.register(HITItem, HITItemAdmin)
