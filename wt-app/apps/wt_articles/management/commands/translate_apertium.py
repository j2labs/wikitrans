from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime

from wt_articles import APERTIUM
from wt_articles.utils import apertium_translator
from wt_articles.models import TranslationRequest, TranslatedArticle
from wt_articles.models import SourceSentence, TranslatedSentence

class Command(NoArgsCommand):
    help = "Updates the texts for wikipedia articles of interest"
    requires_model_validation = False

    def handle_noargs(self, **options):
        t = apertium_translator()
        reqs = TranslationRequest.objects.filter(translator=APERTIUM)
        completed_reqs = list()
        ta_sentences = list()
        for req in reqs:
            req_sentences = req.article.sourcesentence_set.all()
            translated_title = t.translate(req.article.title,
                                           source=req.article.language,
                                           target=req.target_language)
            for s in req_sentences:
                translated = t.translate(s.text,
                                         source=s.article.language,
                                         target=req.target_language)
                ts = TranslatedSentence(segment_id=s.segment_id,
                                        source_sentence=s,
                                        text=translated,
                                        translated_by=t.name,
                                        translation_date=datetime.now(),
                                        language=req.target_language,
                                        best=True,
                                        end_of_paragraph=s.end_of_paragraph)
                ta_sentences.append(ts)
            ta = TranslatedArticle()
            ta.article = req.article
            ta.title = translated_title
            ta.timestamp = datetime.now()
            ta.language = req.target_language
            try:
                ta.save()
                for ts in ta_sentences:
                    ts.save()
                ta.sentences = ta_sentences
                ta.save()
                completed_reqs.append(req)
                for cr in completed_reqs:
                    cr.delete()
            except Exception as e:
                print type(e)
                print e.args
                ta.delete()
                for ts in ta_sentences:
                    ts.delete()
                raise

