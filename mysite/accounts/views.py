
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.views.generic import ListView, FormView, TemplateView, DetailView
from django.urls import reverse_lazy
from .models import Address, User
from .forms import (
    AddressForm, UserUpdateForm, RegistrationForm, LoginForm, 
    PasswordChangeForm, PasswordResetRequestForm, PasswordResetConfirmForm
)
from .tasks import send_confirmation_email, send_password_reset_email
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user

class ProfileEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    success_message = _("Profile updated successfully")

    def get_object(self, queryset=None):
        return self.request.user

class LoginView(AuthLoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('accounts:account_update')


def logout_view(request):
    logout(request)
    return redirect('/') # Redirect to the homepage

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('accounts:register_done')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False # Deactivate account until email confirmation
        user.save()

        # Schedule the confirmation email
        send_confirmation_email.delay(user.pk)
        
        return super().form_valid(form)

class RegisterDoneView(TemplateView):
    template_name = 'accounts/register_done.html'

def confirm_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('accounts:confirm_email_success')
    else:
        return redirect('accounts:confirm_email_failed')

class EmailConfirmationSuccessView(TemplateView):
    template_name = 'accounts/confirm_email_success.html'

class EmailConfirmationFailedView(TemplateView):
    template_name = 'accounts/confirm_email_failed.html'

class PasswordChangeView(LoginRequiredMixin, FormView):
    template_name = 'accounts/password_change.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('accounts:profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        user.set_password(form.cleaned_data['new_password1'])
        user.save()
        update_session_auth_hash(self.request, user)  # Important!
        messages.success(self.request, _('Your password was successfully updated!'))
        return super().form_valid(form)

class PasswordResetRequestView(FormView):
    template_name = 'accounts/password_reset_request.html'
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy('accounts:password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            send_password_reset_email.delay(user.pk)
        except User.DoesNotExist:
            # Don't reveal that the user does not exist
            pass
        return super().form_valid(form)

class PasswordResetRequestDoneView(TemplateView):
    template_name = 'accounts/password_reset_done.html'

class PasswordResetConfirmView(FormView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = PasswordResetConfirmForm
    success_url = reverse_lazy('accounts:password_reset_complete')

    def dispatch(self, request, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(kwargs['uidb64']))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            self.user = None

        if self.user is None or not default_token_generator.check_token(self.user, kwargs['token']):
            return redirect(reverse_lazy('accounts:password_reset_invalid'))
        
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, _('Your password has been set.'))
        return super().form_valid(form)

class PasswordResetCompleteView(TemplateView):
    template_name = 'accounts/password_reset_complete.html'

class PasswordResetInvalidView(TemplateView):
    template_name = 'accounts/password_reset_invalid.html'


class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    template_name = 'accounts/address_list.html'
    context_object_name = 'addresses'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

class AddressCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Address
    form_class = AddressForm
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('accounts:address_list')
    success_message = _("Address created successfully")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class AddressUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('accounts:address_list')
    success_message = _("Address updated successfully")

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


@login_required
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        return redirect('accounts:address_list')
    return render(request, 'accounts/address/confirm_delete.html', {'address': address})

@login_required
def set_default_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.is_default = True
    address.save()
    return redirect('accounts:address_list')



@login_required
def account_update(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:account_update') # Redirect to the same page to show changes
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/update_form.html', {'form': form})
