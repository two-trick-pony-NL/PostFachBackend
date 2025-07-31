from rest_framework import generics, permissions
from django.http import FileResponse, Http404 
from .models import Email, EmailThread, EmailAttachment
from .serializers import EmailSerializer, EmailThreadSerializer, SendEmailSerializer, EmailAttachmentSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from email_integrations.tasks import send_email_task
from email_integrations.models import ImapIntegration
import django_rq
import uuid
from django.utils.timezone import now
from users.models import Contact, UserProfile
from django.utils import timezone
from datetime import timedelta

class EmailListView(generics.ListAPIView):
    serializer_class = EmailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_profile = UserProfile.objects.get(id=self.request.user.id)
        return (
            Email.objects.filter(owner=user_profile)
            .select_related('from_contact', 'thread')
            .prefetch_related('to_contacts', 'attachments')
            .order_by('-received_at')
        )


class EmailDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = EmailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user_profile = UserProfile.objects.get(id=self.request.user.id)
        return (
            Email.objects.filter(owner=user_profile)
            .select_related('from_contact', 'thread')
            .prefetch_related('to_contacts', 'attachments')
        )

    def perform_update(self, serializer):
        allowed_fields = {'is_read', 'is_starred'}
        update_data = {field: self.request.data.get(field) for field in allowed_fields if field in self.request.data}
        serializer.save(**update_data)


class EmailThreadListView(generics.ListAPIView):
    serializer_class = EmailThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_profile = UserProfile.objects.get(id=self.request.user.id)
        return (
            EmailThread.objects.filter(owner=user_profile)
            .prefetch_related(
                'emails__from_contact',
                'emails__to_contacts',
                'emails__attachments'
            )
            .order_by('-created_at')
        )


class EmailThreadDetailView(generics.RetrieveAPIView):
    serializer_class = EmailThreadSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user_profile = UserProfile.objects.get(id=self.request.user.id)
        return (
            EmailThread.objects.filter(owner=user_profile)
            .prefetch_related(
                'emails__from_contact',
                'emails__to_contacts',
                'emails__attachments'
            )
        )


class SendEmailView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SendEmailSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            integration = ImapIntegration.objects.get(pk=data['integration_id'])
        except ImapIntegration.DoesNotExist:
            return Response({"error": "Invalid integration_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Create thread or find one (optional: can be a new thread or none)
        thread = EmailThread.objects.create(owner=integration.user, subject=data['subject'])

        # Create the email record immediately
        email_obj = Email.objects.create(
            owner=integration.user,
            thread=thread,
            from_email=integration.email,
            subject=data['subject'],
            body=data['body_text'],
            html_body=data.get('body_html', ''),
            direction='OUT',
            message_id=f"local-{uuid.uuid4()}",  # temp local id, can be updated later
            received_at=now(),
            status='queued',
        )

        # Create or link contacts for recipients
        for to_email in data['to_emails']:
            contact, _ = Contact.objects.get_or_create(owner=integration.user, email=to_email)
            email_obj.to_contacts.add(contact)

        # Enqueue sending task with the email id
        queue = django_rq.get_queue('outbound')
        queue.enqueue(
            send_email_task,
            integration_id=str(integration.id),
            from_email=integration.email,
            to_emails=data['to_emails'],
            subject=data['subject'],
            body_text=data['body_text'],
            body_html=data.get('body_html', ''),
            attachments=data.get('attachments', None),
            from_name=data.get('from_name'),
            email_id=str(email_obj.id),
        )

        return Response({"status": "Email queued for sending", "email_id": str(email_obj.id)}, status=status.HTTP_202_ACCEPTED)
    
class EmailAttachmentListView(generics.ListAPIView):
    serializer_class = EmailAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_profile = UserProfile.objects.get(id=self.request.user.id)
        return EmailAttachment.objects.filter(email__owner=user_profile).select_related('email').order_by('-created_at')


class EmailAttachmentDetailView(generics.RetrieveAPIView):
    serializer_class = EmailAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user_profile = UserProfile.objects.get(id=self.request.user.id)
        return EmailAttachment.objects.filter(email__owner=user_profile).select_related('email')
    
class EmailAttachmentDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        try:
            user_profile = UserProfile.objects.get(id=request.user.id)
            attachment = EmailAttachment.objects.get(id=id, email__owner=user_profile)

            if not attachment.file:
                raise Http404("No file found on this attachment.")

            return FileResponse(attachment.file.open('rb'), as_attachment=True, filename=attachment.filename)
        except EmailAttachment.DoesNotExist:
            raise Http404("Attachment not found.")
        



def EmailAttachmentPublicDownloadView(request, token):
    user_uuid = token[:36]
    public_token = token[37:]
    user = UserProfile.objects.get(pk=user_uuid)
    attachment = EmailAttachment.objects.get(owner=user, public_token=public_token)
    
    if not attachment:
        raise Http404("Attachment not found or invalid token.")

    now = timezone.now()

    if now - attachment.public_token_created > timedelta(days=7):
        attachment.rotate_token()
        raise Http404("Link expired")

    if attachment.download_count >= 5:
        attachment.rotate_token()
        raise Http404("Download limit reached")

    attachment.download_count += 1
    attachment.save(update_fields=['download_count'])

    if not attachment.file:
        raise Http404("No file found on this attachment.")

    return FileResponse(attachment.file.open('rb'), as_attachment=True, filename=attachment.filename)
