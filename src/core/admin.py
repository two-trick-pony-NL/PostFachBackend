# rqadmin/admin.py
from django.contrib import admin
from .models import DummyModel

@admin.register(DummyModel)
class DummyModelAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect
        return redirect('/django-rq/')
