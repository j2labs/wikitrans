from wt_articles.models import ArticleOfInterest, TranslationRequest, FeaturedTranslation
from wt_articles.models import SourceArticle, SourceSentence
from wt_articles.models import TranslatedArticle, TranslatedSentence, MTurkTranslatedSentence
from django.contrib import admin

class ArticleOfInterestAdmin(admin.ModelAdmin):
    list_display = ('title', 'title_language', 'target_language',)
    search_fields = ('title', 'title_language', 'target_language',)

class TranslationRequestAdmin(admin.ModelAdmin):
    list_display = ('article', 'target_language', 'translator',)
    search_fields = ('article', 'target_language', 'translator',)

class SourceArticleAdmin(admin.ModelAdmin):
    list_display = ('title','language',)
    search_fields = ('title','language','source_url','source_text',)

class SourceSentenceAdmin(admin.ModelAdmin):
    list_display = ('article','text','segment_id',)
    search_fields = ('article','text',)

class TranslatedArticleAdmin(admin.ModelAdmin):
    list_display = ('article', 'language', 'timestamp', 'approved',)
    search_fields = ('article', 'title', 'language', 'timestamp', 'approved',)

class TranslatedSentenceAdmin(admin.ModelAdmin):
    list_display = ('segment_id','translation_date','text', 'approved',)
    search_fields = ('segment_id','translation_date','text', 'approved',)

class FeaturedTranslationAdmin(admin.ModelAdmin):
    list_display = ('article','featured_date',)
    
class MTurkTranslatedSentenceAdmin(TranslatedArticleAdmin):
    list_display = ('segment_id','translation_date','text', 'approved',)
    search_fields = ('segment_id','translation_date','text', 'approved',)
    
admin.site.register(ArticleOfInterest, ArticleOfInterestAdmin)
admin.site.register(TranslationRequest, TranslationRequestAdmin)
admin.site.register(SourceArticle, SourceArticleAdmin)
admin.site.register(SourceSentence, SourceSentenceAdmin)
admin.site.register(TranslatedArticle, TranslatedArticleAdmin)
admin.site.register(TranslatedSentence, TranslatedSentenceAdmin)
admin.site.register(FeaturedTranslation, FeaturedTranslationAdmin)
admin.site.register(MTurkTranslatedSentence, MTurkTranslatedSentenceAdmin)
