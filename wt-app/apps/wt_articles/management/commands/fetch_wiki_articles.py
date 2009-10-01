from django.core.management.base import NoArgsCommand, CommandError
from wt_articles.models import ArticleOfInterest, SourceArticle
from datetime import datetime

import urllib
import simplejson

WIKIPEDIA_API_URL = 'http://%s.wikipedia.org/w/api.php?%s'

def fetch_wikipedia_texts(title, language):
    query = urllib.urlencode({'action': 'parse',
                              'page': title,
                              'format': 'json'})
    url = WIKIPEDIA_API_URL % (language, query)
    search_results = urllib.urlopen(url)
    print url
    json = simplejson.loads(search_results.read())
    html = json['parse']['text']['*']
    revid = json['parse']['revid']
    return (revid, html)

class Command(NoArgsCommand):
    help = "Updates the texts for wikipedia articles of interest"

    requires_model_validation = False

    def handle_noargs(self, **options):
        articles_of_interest = ArticleOfInterest.objects.all()
        for article in articles_of_interest:
            version_html = fetch_wikipedia_texts(article.title, article.language)
            source_article = SourceArticle(title=article.title,
                                           language=article.language,
                                           source_text=version_html[1],
                                           import_date=datetime.now(),
                                           doc_id=version_html[0])
            source_article.save()
