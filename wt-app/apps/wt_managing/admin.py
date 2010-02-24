from wt_managing.models import ArticleReview, SentenceReview
from django.contrib import admin

class SentenceReviewAdmin(admin.ModelAdmin):
    list_display        = ('articlereview', 'review_date', 'segment_id', 'status',)
    search_fields       = ('articlereview', 'review_date', 'segment_id', 'status',)

class ArticleReviewAdmin(admin.ModelAdmin):
    list_display        = ('translated_article', 'start_date', 'finished_date', 'status',)
    search_fields       = ('translated_article', 'start_date', 'finished_date', 'status',)

admin.site.register(SentenceReview, SentenceReviewAdmin)
admin.site.register(ArticleReview, ArticleReviewAdmin)
