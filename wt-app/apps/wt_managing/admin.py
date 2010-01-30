from wt_managing.models import TranslationReview
from django.contrib import admin

class TranslationReviewAdmin(admin.ModelAdmin):
    list_display        = ('user', 'review_date', 'accepted', 'status')
    search_fields       = ('user', 'review_date', 'accepted', 'status', 'rating',)

admin.site.register(TranslationReview, TranslationReviewAdmin)
