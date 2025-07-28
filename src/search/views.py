from rest_framework.views import APIView
from rest_framework.response import Response
from .queries import autocomplete_contacts

class ContactAutocompleteView(APIView):
    def get(self, request):
        q = request.query_params.get("q", "")
        if not q:
            return Response([])
        user_id = request.user.id
        suggestions = autocomplete_contacts(q, user_id)
        return Response(suggestions)
