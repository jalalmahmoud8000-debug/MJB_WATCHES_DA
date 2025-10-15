
from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("faq/", views.FAQView.as_view(), name="faq"),
    path("terms/", views.TermsView.as_view(), name="terms"),
    path("policy/", views.PrivacyPolicyView.as_view(), name="policy"),
]
