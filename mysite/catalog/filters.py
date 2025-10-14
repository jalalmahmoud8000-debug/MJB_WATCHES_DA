
import django_filters
from .models import Product, Brand, Category
from django import forms
from django.db.models import Q

class ProductFilter(django_filters.FilterSet):
    # A custom text search filter. It searches across product name and description.
    search = django_filters.CharFilter(method='search_filter', label="", widget=forms.TextInput(attrs={'placeholder': 'Search products...'}))

    # Filter for price range. The 'variants__price' assumes a related ProductVariant model.
    price = django_filters.RangeFilter(field_name='variants__price', label='Price Range')

    # Filter by brand using a dropdown
    brand = django_filters.ModelChoiceFilter(
        queryset=Brand.objects.all(),
        widget=forms.Select,
        label='Brand'
    )
    
    # Filter by category using a dropdown
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        widget=forms.Select,
        label='Category'
    )

    # A choice filter for sorting
    ordering = django_filters.OrderingFilter(
        label='Sort By',
        fields=(
            ('created_at', 'newest'),
            ('-created_at', 'oldest'),
            ('variants__price', 'price_asc'),
            ('-variants__price', 'price_desc'),
        ),
        field_labels={
            'created_at': 'Newest first',
            '-created_at': 'Oldest first',
            'variants__price': 'Price: Low to High',
            '-variants__price': 'Price: High to Low',
        }
    )

    class Meta:
        model = Product
        fields = ['search', 'price', 'brand', 'category']

    def search_filter(self, queryset, name, value):
        """ Custom filter method to search in name and description. """
        if not value:
            return queryset
        # Use Q objects to create an OR query
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        ).distinct()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide the search field from the filter form displayed in the sidebar,
        # as it's already in the navbar.
        if 'search' in self.form.fields:
            self.form.fields['search'].widget = forms.HiddenInput()
