
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import ContactForm


class AboutView(TemplateView):
    template_name = "pages/about.html"


class ContactView(FormView):
    template_name = "pages/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("pages:contact")

    def form_valid(self, form):
        form.save()
        # Send email
        send_mail(
            subject=f'Contact Form Inquiry: {form.cleaned_data["subject"]}',
            message=form.cleaned_data["message"],
            from_email=form.cleaned_data["email"],
            recipient_list=["contact@example.com"],  # Replace with your contact email
        )
        messages.success(
            self.request, "Thank you for your message. We will get back to you shortly."
        )
        return super().form_valid(form)


class FAQView(TemplateView):
    template_name = "pages/faq.html"


class TermsView(TemplateView):
    template_name = "pages/terms.html"


class PrivacyPolicyView(TemplateView):
    template_name = "pages/policy.html"
