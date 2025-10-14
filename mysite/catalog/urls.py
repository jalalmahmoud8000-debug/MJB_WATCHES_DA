
from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    # URL for the main product list/filter page
    path('products/', views.product_list, name='product_list'),
    
    # URL for a single product detail page
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),

    # URL for the category list page
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
]
