
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from orders.models import Order, Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentSelectView(TemplateView):
    template_name = 'payments/payment_select.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_id'] = self.kwargs.get('order_id')
        return context


class StripePaymentView(View):
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': f'Order #{order.id}',
                            },
                            'unit_amount': int(order.total * 100),
                        },
                        'quantity': 1,
                    }
                ],
                mode='payment',
                success_url=request.build_absolute_uri(
                    f'/payments/success/{order.id}/'),
                cancel_url=request.build_absolute_uri(
                    f'/payments/failed/{order.id}/'),
            )
            Payment.objects.create(
                order=order,
                provider='Stripe',
                transaction_id=checkout_session.id,
                amount=order.total
            )
            return JsonResponse({'id': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        payment = get_object_or_404(
            Payment, transaction_id=session.id)
        payment.status = 'SUCCEEDED'
        payment.save()
        order = payment.order
        order.status = 'PROCESSING'
        order.save()

    return HttpResponse(status=200)


class PaymentSuccessView(TemplateView):
    template_name = 'payments/payment_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = get_object_or_404(Order, id=self.kwargs.get('order_id'))
        return context


class PaymentFailedView(TemplateView):
    template_name = 'payments/payment_failed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = get_object_or_404(Order, id=self.kwargs.get('order_id'))
        return context
