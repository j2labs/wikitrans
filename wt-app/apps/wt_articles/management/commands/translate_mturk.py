from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime

from wt_articles import MECHANICAL_TURK
from wt_articles.mturk import handle_translation_request
from wt_articles.models import TranslationRequest, TranslatedArticle
from wt_articles.models import SourceSentence, TranslatedSentence

class Command(NoArgsCommand):
    help = """
    Updates the texts for wikipedia articles of interest using
    Amazon Mechanical Turk
    """
    requires_model_validation = False

    def handle_noargs(self, **options):
        reqs = TranslationRequest.objects.filter(translator=MECHANICAL_TURK)
        for req in reqs:
            try:
                handle_translation_request(req)
            except Exception as e:
                print type(e)
                print e.args
                raise
        print '\n%s mechanical turk translation requests handled' % len(reqs)
        
