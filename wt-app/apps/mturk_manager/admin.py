from mturk_manager.models import TaskConfig, TaskItem, TaskAttribute
from mturk_manager.models import HITItem, AssignmentItem
from django.contrib import admin

class HITItemInline(admin.TabularInline):
    model = HITItem
    extra = 0

class TaskAttributeInline(admin.TabularInline):
    model = TaskAttribute
    extra = 1

class TaskConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'reward', 'bonus',)
    search_fields = ('name', 'title', 'description', 'reward', 'bonus',)

class TaskAttributeAdmin(admin.ModelAdmin):
    list_display = ('task_item', 'key', 'value',)
    search_fields = ('task_item', 'key', 'value',)

class TaskItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'creation_date', 'status',)
    search_fields = ('hitid', 'status',)
    inlines = [HITItemInline, TaskAttributeInline]

class HITItemAdmin(admin.ModelAdmin):
    list_display = ('hitid', 'creation_date', 'status',)
    search_fields = ('hitid', 'status',)

class AssignmentItemAdmin(admin.ModelAdmin):
    list_display = ('assignment_id', 'accept_time', 'status', 'worker_id',)
    search_fields = ('assignment_id', 'accept_time', 'status', 'worker_id',)

admin.site.register(TaskConfig, TaskConfigAdmin)    
admin.site.register(TaskAttribute, TaskAttributeAdmin)    
admin.site.register(TaskItem, TaskItemAdmin)    
admin.site.register(HITItem, HITItemAdmin)
admin.site.register(AssignmentItem, AssignmentItemAdmin)
