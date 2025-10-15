
from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    # URL for the main product list/filter page
    path('products/', views.ProductListView.as_view(), name='product_list'),
    
    # URL for a single product detail page
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),

    # URL for the category list page
    path('categories/', views.CategoryListView.as_view(), name='category_list'),

    # URL for a single category's product list
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),

    path('search/', views.SearchResultsView.as_view(), name='search_results'),

    path('brands/', views.BrandListView.as_view(), name='brand_list'),

    path('brands/<slug:slug>/', views.BrandDetailView.as_view(), name='brand_detail'),

    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),

    path('wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),

    path('wishlist/remove/', views.remove_from_wishlist, name='remove_from_wishlist'),
]
