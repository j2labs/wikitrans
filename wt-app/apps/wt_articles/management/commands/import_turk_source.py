from django.db.transaction import commit_on_success
from django.core.management.base import BaseCommand
from django.core.management.color import no_style

from wt_articles.models import SourceSentence, SourceArticle

import sys
import os
import csv
import re
from optparse import make_option
from datetime import datetime

try:
    set
except NameError:
    from sets import Set as set   # Python 2.3 fallback

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--articles-file', dest='articles_file',
            help='File containing article titles: hi_articles'),
        make_option('--ids-file', dest='ids_file', 
            help='File containing article ids: hi_articles.ids'),
        make_option('--source-file', dest='source_file',
            help='The source imput for Amazon: hindi_wikipedia_feature_article_to_translate-2010-02-13T1051.csv'),
    )
    help = 'Installs the named mechanical turk output files in the database.'
    args = "--articles-file <file> --ids-file <file> --source-file <file>"

    def handle(self, *labels, **options):
        from django.db.models import get_apps
        from django.core import serializers
        from django.db import connection, transaction
        from django.conf import settings

        self.style = no_style()

        articles_file = options.get('articles_file', None)
        ids_file = options.get('ids_file', None)
        source_file = options.get('source_file', None)
        error = False
        if not os.path.exists(articles_file):
            print 'artficles-file does not exist'
            return
        if not os.path.exists(ids_file):
            print 'ids-file does not exist'
            return
        if not os.path.exists(source_file):
            print 'source-file-file does not exist'
            return

        # Generate dictionary of article id => article title
        article_names = self.parse_articles_file(articles_file)
        article_ids = self.parse_ids_file(ids_file)
        article_id_map = {}
        for name, aid in zip(article_names, article_ids):
            article_id_map[aid.strip()] = name.strip()

        return self.parse_source_file(source_file, article_id_map)

    def parse_articles_file(self, articles_file):
        f = open(articles_file, 'r')
        return f.readlines()

    def parse_ids_file(self, ids_file):
        f = open(ids_file, 'r')
        return f.readlines()

    @commit_on_success
    def parse_source_file(self, source_file, article_id_map):
        f = open(source_file, 'r')
        csv_reader = csv.reader(f)
        headers = csv_reader.next()
        header_map = {}
        for i,h in enumerate(headers):
            header_map[h] = i

        # The headers are uniform in this file
        # lang,(seg_id1,tag1,seg1,img_url1,machine_translation1),...,(seg_idn,...)
        sa = SourceArticle()
        cur_aid = -1
        language = None
        segments = ['seg_id%s' % i for i in xrange(1,11)]
        for line in csv_reader:
            segment_offsets = [(header_map[seg]) for seg in segments]
            for offs in segment_offsets:
                try:
                    (aid, seg_id) = line[offs].split('_')
                except IndexError:
                    # treating this basically like an eof

                    try:
                        sa.save(manually_splitting=True)
                    except UnicodeDecodeError:
                        print 'Argh! Unicode issues (1)...'
                        sa.delete()
                    break
                
                if int(seg_id) == 0:
                    sa.sentences_processed = True
                    language = line[0]
                    try:
                        self.save_sentence(sa, line[0], aid, article_id_map[aid])
                    except UnicodeDecodeError:
                        print 'Argh! Unicode issues...(2)'
                        sa.delete()

                    # make a new sa object
                    sa = SourceArticle()
                sa.save(manually_splitting=True) # get an id
                #tag = 'tag'
                tag = line[(offs + 1)]
                #seg = 'seg'
                seg = line[(offs + 2)]
                ss = SourceSentence()
                ss.article = sa
                ss.text = seg
                ss.segment_id = seg_id
                ss.end_of_paragraph = re.search("LastSentence", seg) or False
                ss.save()
                print '%s :: %s :: %s' % (aid, seg_id, tag)
            
        #for line in csv_reader:
        #    print 'JD : %s' % line
            
    def save_sentence(self, sa, language, doc_id, title):
        sa.source_text = 'Not sure how to handle this yet'
        sa.language = language
        sa.doc_id = doc_id 
        sa.timestamp = datetime.now()
        sa.title = title
        sa.save(manually_splitting=True)

        
