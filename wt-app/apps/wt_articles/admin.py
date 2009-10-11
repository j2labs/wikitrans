from wt_articles.models import ArticleOfInterest
from wt_articles.models import SourceArticle, SourceSentence
from wt_articles.models import TranslatedArticle, TranslatedSentence
from django.contrib import admin

class ArticleOfInterestAdmin(admin.ModelAdmin):
    list_display = ('title', 'title_language', 'target_language',)
    search_fields = ('title', 'title_language', 'target_language',)

class SourceArticleAdmin(admin.ModelAdmin):
    list_display = ('title','source_language',)
    search_fields = ('title','source_language','source_url','source_text',)

class SourceSentenceAdmin(admin.ModelAdmin):
    list_display = ('article','text','segment_id',)
    search_fields = ('article','text',)

class TranslatedArticleAdmin(admin.ModelAdmin):
    list_display = ('article', 'language', 'timestamp',)
    search_fields = ('article', 'title', 'language', 'timestamp',)

class TranslatedSentenceAdmin(admin.ModelAdmin):
    list_display = ('segment_id','translation_date','translation', 'best',)
    search_fields = ('segment_id','translation_date','translation', 'best',)
    
admin.site.register(ArticleOfInterest, ArticleOfInterestAdmin)
admin.site.register(SourceArticle, SourceArticleAdmin)
admin.site.register(SourceSentence, SourceSentenceAdmin)
admin.site.register(TranslatedArticle, TranslatedArticleAdmin)
admin.site.register(TranslatedSentence, TranslatedSentenceAdmin)
