from wt_articles.models import ArticleOfInterest,SourceArticle,SourceSentence
from django.contrib import admin

class ArticleOfInterestAdmin(admin.ModelAdmin):
    list_display = ('title', 'title_language', 'target_language',)
    search_fields = ('title', 'title_language', 'target_language',)

class SourceArticleAdmin(admin.ModelAdmin):
    list_display = ('title','language',)
    search_fields = ('title','language','source_url','source_text',)

class SourceSentenceAdmin(admin.ModelAdmin):
    list_display = ('article','text','segment_id',)
    search_fields = ('article','text',)

admin.site.register(ArticleOfInterest, ArticleOfInterestAdmin)
admin.site.register(SourceArticle, SourceArticleAdmin)
admin.site.register(SourceSentence, SourceSentenceAdmin)
