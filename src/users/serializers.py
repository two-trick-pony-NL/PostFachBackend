# users/serializers.py
from rest_framework import serializers
from .models import UserProfile, Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'email', 'display_name','always_notify', 'muted', 'marked_as_spam',
            'important', 'whitelist'
        ]
        
        
class ContactUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'display_name',
            'always_notify', 'muted', 'marked_as_spam',
            'important', 'whitelist'
        ]

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name', 'public_username']
