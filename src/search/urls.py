# search/urls.py
from django.urls import path
from .views import ContactAutocompleteView

urlpatterns = [
    path("/contacts/autocomplete/", ContactAutocompleteView.as_view(), name="contact-autocomplete"),
]
