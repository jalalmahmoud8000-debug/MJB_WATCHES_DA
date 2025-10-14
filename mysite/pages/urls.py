
from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('faqs/', views.FAQsView.as_view(), name='faqs'),
    path('contact/', views.contact, name='contact'),
    path('contact/thanks/', views.ContactThanksView.as_view(), name='contact_thanks'),
]
