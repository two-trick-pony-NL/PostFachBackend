# core/authentication.py
from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication, exceptions
from supabase import create_client
import os
import jwt

SUPABASE_URL = os.getenv("SUPABASE_API_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_JWT_KEY_SERVICE_ROLE")
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

class SupabaseUser:
    def __init__(self, user_id, email):
        self.id = user_id
        self.email = email
        self.is_authenticated = True

class SupabaseJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]
        try:
            # Decode JWT without verifying signature to extract user info first
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get("sub")
            email = decoded.get("email")

            # Verify token with Supabase
            response = supabase.auth.get_user(token)
            if not response.user or response.user.id != user_id:
                raise exceptions.AuthenticationFailed("Invalid token or user")

            user = SupabaseUser(user_id=user_id, email=email)
            return (user, token)

        except Exception as e:
            raise exceptions.AuthenticationFailed(f"Invalid token: {str(e)}")

