
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.admin.views.decorators import staff_member_required

from .models import Review, Product


class ReviewListView(ListView):
    model = Review
    template_name = 'product_reviews/review_list.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        self.product = get_object_or_404(
            Product, id=self.kwargs['product_id'])
        return Review.objects.filter(product=self.product, status=Review.APPROVED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context


class CreateReviewView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ['rating', 'title', 'body']
    template_name = 'product_reviews/create_review.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.product = get_object_or_404(
            Product, id=self.kwargs['product_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('product_reviews:review_list',
                            kwargs={'product_id': self.object.product.id})


class EditReviewView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    fields = ['rating', 'title', 'body']
    template_name = 'product_reviews/edit_review.html'

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user

    def get_success_url(self):
        return reverse_lazy('product_reviews:review_list',
                            kwargs={'product_id': self.object.product.id})


class DeleteReviewView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = 'product_reviews/delete_review.html'

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user

    def get_success_url(self):
        return reverse_lazy('product_reviews:review_list',
                            kwargs={'product_id': self.object.product.id})


@staff_member_required
def approve_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.status = Review.APPROVED
    review.save()
    return redirect(reverse_lazy('product_reviews:review_list',
                                kwargs={'product_id': review.product.id}))
