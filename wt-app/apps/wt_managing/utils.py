from django.utils.safestring import SafeUnicode

from wt_articles.models import TranslatedArticle

def user_compatible_translations(user, article_model=TranslatedArticle):
    profile = user.get_profile()
    languages = set([lc.language for lc in user.languagecompetancy_set.all()])

    languages.add(profile.native_language)
    languages.add(profile.display_language)
    
    source_articles = set(article_model.objects.filter(language__in=languages))
    return source_articles


