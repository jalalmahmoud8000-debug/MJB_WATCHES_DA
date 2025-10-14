
from celery import shared_task
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import User

@shared_task
def send_confirmation_email(user_pk):
    """
    Asynchronously sends a confirmation email to a new user.
    """
    try:
        user = User.objects.get(pk=user_pk)
        
        # Generate a token and encode the user's pk
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Build the confirmation URL
        confirmation_url = reverse('accounts:confirm_email', kwargs={'uidb64': uid, 'token': token})
        full_confirmation_url = f'http://localhost:8000{confirmation_url}' # Replace with your domain in production
        
        # Email subject and message
        subject = 'Activate Your Account'
        message = f"""
        Hi {user.email},

        Thank you for creating an account. Please click the link below to activate your account:

        {full_confirmation_url}

        If you did not sign up for this account, you can ignore this email.

        Thanks,
        The Team
        """
        
        # Send the email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return f"Confirmation email sent to {user.email}"
    except User.DoesNotExist:
        return f"User with pk {user_pk} not found."
    except Exception as e:
        # Log the exception for debugging
        return f"Failed to send confirmation email to user {user_pk}: {e}"

@shared_task
def send_password_reset_email(user_pk):
    """
    Asynchronously sends a password reset email to a user.
    """
    try:
        user = User.objects.get(pk=user_pk)
        
        # Generate a token and encode the user's pk
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Build the password reset URL
        reset_url = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        full_reset_url = f'http://localhost:8000{reset_url}' # Replace with your domain in production
        
        # Email subject and message
        subject = 'Reset Your Password'
        message = f"""
        Hi {user.email},

        We received a request to reset your password. Please click the link below to set a new password:

        {full_reset_url}

        If you did not request a password reset, you can ignore this email.

        Thanks,
        The Team
        """
        
        # Send the email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return f"Password reset email sent to {user.email}"
    except User.DoesNotExist:
        return f"User with pk {user_pk} not found."
    except Exception as e:
        # Log the exception for debugging
        return f"Failed to send password reset email to user {user_pk}: {e}"
