import jwt
from django.http import JsonResponse
from .settings import SUPABASE_JWT_KEY_SERVICE_ROLE


class SupabaseAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SUPABASE_JWT_KEY_SERVICE_ROLE, algorithms=['HS256'], audience='authenticated')
            request.user_id = payload['sub']  # Supabase user ID
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        response = self.get_response(request)
        return response
