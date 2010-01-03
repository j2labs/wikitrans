from datetime import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _

from wt_articles.models import SourceSentence,TranslatedSentence
from wt_articles.models import TranslatedArticle,TranslationRequest
from wt_articles import DEFAULT_TRANNY
from django import forms
from django.forms.formsets import formset_factory

class TranslatedSentenceMappingForm(forms.ModelForm):
    source_sentence = forms.ModelChoiceField(SourceSentence.objects.all(),
                                             widget=forms.HiddenInput())
    text = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = TranslatedSentence
        exclude = ('segment_id','translated_by','language',
                   'translation_date','best','end_of_paragraph')

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(TranslatedSentenceMappingForm, self).__init__(*args, **kwargs)


class TranslationRequestForm(forms.ModelForm):
    article_name = forms.CharField(label='Article name')
    
    class Meta:
        model = TranslationRequest
        exclude = ('article','date','translator',)

    def __init__(self, translator=DEFAULT_TRANNY, *args, **kwargs):
        super(TranslationRequestForm, self).__init__(*args, **kwargs)


