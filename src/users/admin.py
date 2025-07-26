from django.contrib import admin
from .models import UserProfile, Contact

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'public_username', 'first_name', 'last_name', 'created_at', 'updated_at')
    search_fields = ('public_username', 'first_name', 'last_name', 'supabase_user_id')
    ordering = ('created_at',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'owner')
    search_fields = ('email', 'first_name', 'last_name', 'owner__public_username')
    ordering = ('email',)
