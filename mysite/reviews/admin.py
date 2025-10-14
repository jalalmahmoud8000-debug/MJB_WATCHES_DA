
from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'approved', 'created_at')
    list_filter = ('approved', 'created_at', 'rating')
    search_fields = ('user__email', 'product__name', 'title', 'body')
    list_editable = ('approved',)
    autocomplete_fields = ['product', 'user']
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(approved=True)
    approve_reviews.short_description = "Approve selected reviews"
