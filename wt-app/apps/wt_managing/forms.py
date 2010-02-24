from datetime import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _

from wt_managing.models import SentenceReview

class SentenceReviewForm(forms.ModelForm):
    segment_id = forms.CharField(widget=forms.HiddenInput)
    articlereview = forms.CharField(widget=forms.HiddenInput)
    
    class Meta:
        model = SentenceReview
        fields = ('articlereview', 'segment_id', 'accepted',)
    
    def __init__(self, *args, **kwargs):
        super(SentenceReviewForm, self).__init__(*args, **kwargs)

