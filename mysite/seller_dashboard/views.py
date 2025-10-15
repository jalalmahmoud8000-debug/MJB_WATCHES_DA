
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView

from catalog.models import Product


class ProductListDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Product
    template_name = "seller_dashboard/product_list.html"
    context_object_name = "products"

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return Product.objects.all().order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Products"
        return context
