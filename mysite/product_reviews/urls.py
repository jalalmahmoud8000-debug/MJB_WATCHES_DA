
from django.urls import path

from . import views

app_name = 'product_reviews'

urlpatterns = [
    path('<int:product_id>/reviews/', views.ReviewListView.as_view(),
         name='review_list'),
    path('<int:product_id>/reviews/create/',
         views.CreateReviewView.as_view(), name='create_review'),
    path('reviews/<int:pk>/edit/', views.EditReviewView.as_view(),
         name='edit_review'),
    path('reviews/<int:pk>/delete/', views.DeleteReviewView.as_view(),
         name='delete_review'),
    path('reviews/<int:review_id>/approve/', views.approve_review,
         name='approve_review'),
]
