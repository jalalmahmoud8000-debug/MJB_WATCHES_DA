
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from catalog.models import Product
from .forms import ReviewForm

@login_required
def create_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('catalog:product_detail', slug=product.slug)
    else:
        form = ReviewForm()
    return render(request, 'reviews/create_review.html', {'form': form, 'product': product})
