# core/authentication.py
import jwt
from jwt import PyJWKClient
from rest_framework import authentication, exceptions
from core.settings import SUPABASE_JWKS_URL

jwks_client = PyJWKClient(SUPABASE_JWKS_URL)


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
            # Get the signing key from JWKS
            signing_key = jwks_client.get_signing_key_from_jwt(token).key

            # Decode and verify signature + claims
            decoded = jwt.decode(
                token,
                signing_key,
                algorithms=["ES256"],
                audience="authenticated",
                issuer="https://tnbzfgbtnaatfpiehplp.supabase.co/auth/v1"
            )

            user_id = decoded.get("sub")
            email = decoded.get("email")
            if not user_id or not email:
                raise exceptions.AuthenticationFailed("Invalid token payload")

            return (SupabaseUser(user_id, email), token)

        except Exception as e:
            raise exceptions.AuthenticationFailed(f"Invalid token: {str(e)}")
