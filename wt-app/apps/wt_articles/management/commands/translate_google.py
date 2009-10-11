from django.core.management.base import NoArgsCommand, CommandError
from wt_articles.models import SourceSentence, TranslatedSentence
from datetime import datetime

from wt_articles import google_translator

class Command(NoArgsCommand):
    help = "Updates the texts for wikipedia articles of interest"
    requires_model_validation = False

    def handle_noargs(self, **options):
        t = google_translator()
        source_sentences = SourceSentence.objects.all()
        for i,s in enumerate(source_sentences):
            translated = t.translate(s,
                                     source=s.article.source_language,
                                     target=s.article.target_language)
            ts = TranslatedSentence(segment_id=i,
                                    source_sentence=s,
                                    translation=translated,
                                    translated_by=t.name,
                                    translation_date=datetime.now(),
                                    language=s.article.target_language,
                                    best=True)
            ts.save()

