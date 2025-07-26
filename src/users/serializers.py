# users/serializers.py
from rest_framework import serializers
from .models import UserProfile, Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'email', 'first_name', 'last_name','always_notify', 'muted', 'marked_as_spam',
            'important', 'whitelist'
        ]
        
        
class ContactUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'first_name', 'last_name',
            'always_notify', 'muted', 'marked_as_spam',
            'important', 'whitelist'
        ]

class UserProfileSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name', 'public_username', 'contacts']
