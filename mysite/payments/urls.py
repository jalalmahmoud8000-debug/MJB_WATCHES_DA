
from django.urls import path
from .views import (
    PaymentSelectView,
    StripePaymentView,
    stripe_webhook,
    PaymentSuccessView,
    PaymentFailedView
)

app_name = 'payments'

urlpatterns = [
    path('select/<uuid:order_id>/',
         PaymentSelectView.as_view(), name='payment_select'),
    path('stripe/charge/<uuid:order_id>/',
         StripePaymentView.as_view(), name='stripe_charge'),
    path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),
    path('success/<uuid:order_id>/', PaymentSuccessView.as_view(),
         name='payment_success'),
    path('failed/<uuid:order_id>/', PaymentFailedView.as_view(),
         name='payment_failed'),
]
