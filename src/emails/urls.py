from django.urls import path
from .views import (
    EmailListView, EmailDetailView,
    EmailThreadListView, EmailThreadDetailView,
)

urlpatterns = [
    path('', EmailListView.as_view(), name='email-list'),
    path('<uuid:id>/', EmailDetailView.as_view(), name='email-detail'),
    path('threads/', EmailThreadListView.as_view(), name='thread-list'),
    path('threads/<uuid:id>/', EmailThreadDetailView.as_view(), name='thread-detail'),
]
