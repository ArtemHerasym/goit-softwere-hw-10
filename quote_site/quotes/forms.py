from django.forms import ModelForm

from .models import Author, Quote
from .utils import normalize_quote_text


class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = ["fullname", "born_date", "born_location", "description"]


class QuoteForm(ModelForm):
    class Meta:
        model = Quote
        fields = ["text", "author", "tags"]

    def clean_text(self):
        return normalize_quote_text(self.cleaned_data["text"])
