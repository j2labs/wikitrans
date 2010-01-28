from goopytrans import translate as gtranslate
from apyrtium import translate as atranslate
import nltk.data

from django.utils.safestring import SafeUnicode

from wt_languages.models import TARGET_LANGUAGE, SOURCE_LANGUAGE, BOTH
from wt_languages.models import LanguageCompetancy
from wt_articles.models import SourceArticle, TranslatedArticle
from wt_articles import GOOGLE,APERTIUM
from wt_articles import MECHANICAL_TURK,HUMAN,DEFAULT_TRANNY

class Translator:
    """
    A container class for various translation methods
    """
    def __init__(self, name, func):
        self.name = name
        self.translate = func

    def translate(self, text, source, target):
        self.translate(text, source=source, target=target)

def google_translator():
    return Translator(GOOGLE, gtranslate)

def apertium_translator():
    return Translator(APERTIUM, atranslate)

def _group_sentences(sentences):
    p_groups = []
    prev_s = None
    for s in sentences:
        if prev_s == None or prev_s.end_of_paragraph:
            cur_list = []
            p_groups.append(cur_list)
        cur_list.append(s)
        prev_s = s
    return p_groups

def _format_sentences(sentences, fun):
    sentence_groups = _group_sentences(sentences)
    formatted = ''
    for s_list in sentence_groups:
        raw_text = [(s.text) for s in s_list]
        formatted = formatted + fun(' '.join(raw_text))
    formatted = SafeUnicode(formatted)
    return formatted

def sentences_as_text(sentences):
    format_p = lambda s: '%s\n\n' % (s)
    text = _format_sentences(sentences, format_p)
    return text

def sentences_as_html(sentences):
    format_p = lambda s: '<p>%s</p>' % (s)
    html = _format_sentences(sentences, format_p)
    return html

def _user_compatible_articles(user, article_model, language_direction):
    profile = user.get_profile()
    languages = set([lc.language for lc in
                     user.languagecompetancy_set.exclude(translation_options=language_direction)])

    languages.add(profile.native_language)
    languages.add(profile.display_language)
    
    articles = set(article_model.objects.filter(language__in=languages))
    return articles

def user_compatible_source_articles(user):
    return _user_compatible_articles(user, SourceArticle, TARGET_LANGUAGE)

def user_compatible_target_articles(user):
    return _user_compatible_articles(user, TranslatedArticle, SOURCE_LANGUAGE)

def user_compatible_articles(user):
    source_articles = user_compatible_source_articles(user)
    target_articles = user_compatible_target_articles(user)
    articles = target_articles.union(source_articles)
    return articles

def target_pairs_by_user(user, source):
    target_languages = set([lc.language for lc in
                            user.languagecompetancy_set.exclude(translation_options=SOURCE_LANGUAGE)])
    st_pair_builder = lambda t: (t, '%s-%s' % (source, t))
    pairs = map(st_pair_builder, target_languages)
    return pairs
    

