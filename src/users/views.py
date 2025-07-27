from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions
from rest_framework import status
from emails.serializers import EmailSerializer
from emails.models import Email
from .models import UserProfile, Contact
from .serializers import UserProfileSerializer, ContactSerializer, ContactUpdateSerializer
from emails.tasks import process_incoming_email
import django_rq


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queue = django_rq.get_queue('default')
        queue.enqueue(process_incoming_email, "Hello from background task")
        request.user.id  # adjust if different
        try:
            profile = UserProfile.objects.get(id=request.user.id)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(id=request.user.id)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, created = UserProfile.objects.get_or_create(id=request.user.id)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class ContactDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        return Contact.objects.filter(owner__id=self.request.user.id)

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return ContactUpdateSerializer
        return ContactSerializer



class ContactListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContactSerializer  # <--- add this
    lookup_field = 'id'
    lookup_url_kwarg = 'id' 

    def get_queryset(self):
        return Contact.objects.filter(owner__id=self.request.user.id)


class ContactEmailsListView(generics.ListAPIView):
    serializer_class = EmailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_profile = UserProfile.objects.get(id=self.request.user.id)
        contact_id = self.kwargs['contact_id']
        return Email.objects.filter(
            owner=user_profile
        ).filter(
            from_contact__id=contact_id
        ) | Email.objects.filter(
            owner=user_profile,
            to_contacts__id=contact_id
        )