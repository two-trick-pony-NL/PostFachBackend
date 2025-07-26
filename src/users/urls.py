from django.urls import path
from .views import UserProfileView, ContactDetailView, ContactListView

urlpatterns = [
    path('', UserProfileView.as_view(), name='user-profile'),
    path('contacts/', ContactListView.as_view(), name='contact-list'),
    path('contacts/<uuid:id>/', ContactDetailView.as_view(), name='contact-detail'),  # must match lookup_field='id'    

]
