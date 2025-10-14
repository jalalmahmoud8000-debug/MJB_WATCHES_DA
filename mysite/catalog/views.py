
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product
from .filters import ProductFilter
from cart.models import Cart, CartItem
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = "pages/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_products'] = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
        return context

def product_list(request):
    """ 
    Display a list of products, optionally filtered and sorted.
    This view handles browsing all products, category-specific products, 
    and search results.
    """ 
    # Start with all active products, prefetching primary images
    queryset = Product.objects.filter(is_active=True).prefetch_related('images').distinct()

    # Apply filters from the URL query parameters
    product_filter = ProductFilter(request.GET, queryset=queryset)
    
    # The filtered queryset is what we will work with
    filtered_queryset = product_filter.qs

    # Pagination
    paginator = Paginator(filtered_queryset, 12) # Show 12 products per page
    page_number = request.GET.get('page')
    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    context = {
        'filter': product_filter,
        'products': products,
    }
    return render(request, 'catalog/product/list.html', context)


def product_detail(request, slug):
    """ Display a single product detail page and handle adding to cart. """
    product = get_object_or_404(
        Product.objects.prefetch_related('images', 'variants'), 
        slug=slug, 
        is_active=True
    )
    
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')
        quantity = int(request.POST.get('quantity', 1))
        
        # Since variants are prefetched, we can get it from the product object
        # This avoids an extra database query
        variant = next((v for v in product.variants.all() if v.id == int(variant_id)), None)
        
        if not variant:
            # Handle case where variant_id is invalid
            # You might want to add an error message here
            return redirect('catalog:product_detail', slug=product.slug)

        # Get or create the cart
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                # If cart_id in session is invalid, create a new cart
                cart = Cart.objects.create(user=request.user if request.user.is_authenticated else None)
                request.session['cart_id'] = str(cart.id)
        else:
            cart = Cart.objects.create(user=request.user if request.user.is_authenticated else None)
            request.session['cart_id'] = str(cart.id)
            
        # Get or create the cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # If the item was already in the cart, update the quantity
            cart_item.quantity += quantity
            cart_item.save()
            
        # Redirect to the cart detail page
        return redirect('cart:cart_detail')

    # If it's a GET request, just display the page
    context = {
        'product': product,
    }
    return render(request, 'catalog/product/detail.html', context)
