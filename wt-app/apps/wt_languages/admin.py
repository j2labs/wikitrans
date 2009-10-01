from wt_languages.models import LanguageCompetancy
from django.contrib import admin

class LanguageCompetancyAdmin(admin.ModelAdmin):
    list_display        = ('user', 'language', 'rating')
    search_fields       = ('user', 'language', 'rating')

admin.site.register(LanguageCompetancy, LanguageCompetancyAdmin)
