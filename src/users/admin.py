from django.contrib import admin
from .models import UserProfile, Contact, DummyModel

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'public_username', 'first_name', 'last_name', 'created_at', 'updated_at')
    search_fields = ('public_username', 'first_name', 'last_name', 'supabase_user_id')
    ordering = ('created_at',)




@admin.register(DummyModel)
class DummyModelAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect
        return redirect('/django_rq/')
