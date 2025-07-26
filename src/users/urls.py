from django.urls import path
from .views import UserProfileView, ContactDetailView, ContactListView, ContactEmailsListView

urlpatterns = [
    path('', UserProfileView.as_view(), name='user-profile'),
    path('contacts/', ContactListView.as_view(), name='contact-list'),
    path('contacts/<uuid:id>/', ContactDetailView.as_view(), name='contact-detail'),
    path('contacts/<uuid:contact_id>/emails/', ContactEmailsListView.as_view(), name='contact-emails'),
   

]
