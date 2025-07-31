from django.urls import path
from .views import (
    EmailListView, EmailDetailView,
    EmailThreadListView, EmailThreadDetailView,
    SendEmailView, EmailAttachmentDetailView, EmailAttachmentListView, EmailAttachmentDownloadView, EmailAttachmentPublicDownloadView
)

urlpatterns = [
    path('', EmailListView.as_view(), name='email-list'),
    path('<uuid:id>/', EmailDetailView.as_view(), name='email-detail'),
    path('threads/', EmailThreadListView.as_view(), name='thread-list'),
    path('threads/<uuid:id>/', EmailThreadDetailView.as_view(), name='thread-detail'),
    path('attachments/', EmailAttachmentListView.as_view(), name='attachment-list'),
    path('attachments/<uuid:id>/', EmailAttachmentDetailView.as_view(), name='attachment-detail'),
    path('attachments/<uuid:id>/download/', EmailAttachmentDownloadView.as_view(), name='attachment-download'),
    path('attachments/shared/<str:token>/', EmailAttachmentPublicDownloadView, name='attachment-public-download'),
    path('send/', SendEmailView.as_view(), name='send-email'),


]
