
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from catalog.models import Product

def index(request):
    """View function for home page of site."""

    # Fetch some products to display
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]

    context = {
        'latest_products': latest_products,
    }

    return render(request, 'pages/index.html', context)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            # Send email to admin
            subject = f'New Contact Form Submission: {form.cleaned_data["subject"]}'
            message = f'''
                From: {form.cleaned_data["name"]} <{form.cleaned_data["email"]}>
                Subject: {form.cleaned_data["subject"]}
                Message:
                {form.cleaned_data["message"]}
            '''
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.ADMINS[0][1]])
            return redirect('pages:contact_thanks')
    else:
        form = ContactForm()
    return render(request, 'pages/contact.html', {'form': form})

class ContactThanksView(TemplateView):
    template_name = "pages/contact_thanks.html"

class AboutView(TemplateView):
    template_name = "pages/about.html"

class TermsView(TemplateView):
    template_name = "pages/terms.html"

class PrivacyView(TemplateView):
    template_name = "pages/privacy.html"

class FAQsView(TemplateView):
    template_name = "pages/faqs.html"
