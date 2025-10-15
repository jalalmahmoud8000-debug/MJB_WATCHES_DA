
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import Product, Category, Brand, Wishlist
from .filters import ProductFilter
from cart.models import Cart, CartItem
from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Count
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(TemplateView):
    template_name = "pages/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_products'] = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
        return context

class CategoryListView(ListView):
    model = Category
    template_name = 'catalog/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        """ Returns categories that have associated products. """
        return Category.objects.annotate(product_count=Count('products')).filter(product_count__gt=0)

class BrandListView(ListView):
    model = Brand
    template_name = 'catalog/brand_list.html'
    context_object_name = 'brands'

    def get_queryset(self):
        """ Returns brands that have associated products. """
        return Brand.objects.annotate(product_count=Count('products')).filter(product_count__gt=0)

class CategoryDetailView(ListView):
    model = Product
    template_name = 'catalog/category_detail.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        """Return the products for the current category."""
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Product.objects.filter(category=self.category, is_active=True).prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

class BrandDetailView(ListView):
    model = Product
    template_name = 'catalog/brand_detail.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        """Return the products for the current brand."""
        self.brand = get_object_or_404(Brand, slug=self.kwargs['slug'])
        return Product.objects.filter(brand=self.brand, is_active=True).prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand'] = self.brand
        return context

class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product/list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).prefetch_related('images').distinct()
        self.filter = ProductFilter(self.request.GET, queryset=queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product/detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        """Prefetch related images and variants to optimize performance."""
        return super().get_queryset().prefetch_related('images', 'variants').filter(is_active=True)

    def post(self, request, *args, **kwargs):
        """Handle adding the product variant to the cart."""
        self.object = self.get_object()
        variant_id = request.POST.get('variant_id')
        quantity = int(request.POST.get('quantity', 1))

        if not variant_id:
            # Handle case where no variant is selected
            # You might want to add a message to the user
            return redirect(self.object.get_absolute_url())

        variant = get_object_or_404(self.object.variants, id=variant_id)

        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                cart = self.create_cart(request.user)
        else:
            cart = self.create_cart(request.user)
        
        request.session['cart_id'] = str(cart.id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            
        return redirect('cart:cart_detail')

    def create_cart(self, user):
        """Create a new cart, associated with a user if authenticated."""
        if user.is_authenticated:
            return Cart.objects.create(user=user)
        return Cart.objects.create()

class SearchResultsView(ListView):
    model = Product
    template_name = 'catalog/product/search_results.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query),
                is_active=True
            ).prefetch_related('images').distinct()
        return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class WishlistView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = 'catalog/wishlist.html'
    context_object_name = 'wishlist_items'

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

@login_required
def add_to_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if created:
            return JsonResponse({'status': 'success', 'message': 'Product added to wishlist.'})
        else:
            return JsonResponse({'status': 'warning', 'message': 'Product already in wishlist.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

@login_required
def remove_from_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        try:
            wishlist_item = Wishlist.objects.get(user=request.user, product=product)
            wishlist_item.delete()
            return JsonResponse({'status': 'success', 'message': 'Product removed from wishlist.'})
        except Wishlist.DoesNotExist:
            return JsonResponse({'status': 'warning', 'message': 'Product not in wishlist.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})
