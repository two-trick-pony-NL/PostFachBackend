from django.contrib import admin
from .models import UserProfile, Contact

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'public_username', 'first_name', 'last_name', 'created_at', 'updated_at')
    search_fields = ('public_username', 'first_name', 'last_name', 'supabase_user_id')
    ordering = ('created_at',)

