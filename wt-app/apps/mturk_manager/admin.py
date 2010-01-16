from mturk_manager.models import TaskConfig, TaskItem, HITItem
from django.contrib import admin

class TaskConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'reward', 'bonus',)
    search_fields = ('name', 'title', 'description', 'reward', 'bonus',)

class TaskItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'creation_date', 'status',)
    search_fields = ('hitid', 'status',)

class HITItemAdmin(admin.ModelAdmin):
    list_display = ('hitid', 'creation_date', 'status',)
    search_fields = ('hitid', 'status',)

admin.site.register(TaskConfig, TaskConfigAdmin)    
admin.site.register(TaskItem, TaskItemAdmin)    
admin.site.register(HITItem, HITItemAdmin)
