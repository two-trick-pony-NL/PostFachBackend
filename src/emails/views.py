from rest_framework import generics, permissions
from .models import Email, EmailThread
from .serializers import EmailSerializer, EmailThreadSerializer
from users.models import UserProfile

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
