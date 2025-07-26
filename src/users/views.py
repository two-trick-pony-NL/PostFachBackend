from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions
from rest_framework import status
from .models import UserProfile, Contact
from .serializers import UserProfileSerializer, ContactSerializer, ContactUpdateSerializer

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
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

