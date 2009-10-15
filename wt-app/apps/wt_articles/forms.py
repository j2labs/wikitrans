
from datetime import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _

from wt_articles.models import TranslatedSentence

class TranslatedSentencesForm(forms.ModelForm):
    
    class Meta:
        model = TranslatedSentence
        #exclude = ('user','updated')
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(TranslatedSentencesForm, self).__init__(*args, **kwargs)
