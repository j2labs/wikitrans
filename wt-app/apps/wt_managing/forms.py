from datetime import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _

from wt_managing.models import TranslationReview

class TranslationReviewForm(forms.ModelForm):
    
    class Meta:
        model = TranslationReview
        fields = ('accepted',)
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(TranslationReviewForm, self).__init__(*args, **kwargs)

