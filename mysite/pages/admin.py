
from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('email', 'subject', 'created_at')
    search_fields = ('email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
