from django.contrib import admin
from .models import Document, DocumentShare


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'created_at', 'updated_at']
    list_filter = ['owner']
    search_fields = ['title', 'owner__username']


@admin.register(DocumentShare)
class DocumentShareAdmin(admin.ModelAdmin):
    list_display = ['document', 'shared_with', 'permission']
    list_filter = ['permission']
