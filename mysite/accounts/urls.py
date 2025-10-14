
from django.urls import path
from .views import (
    LoginView,
    logout_view,
    RegisterView, 
    RegisterDoneView,
    confirm_email,
    EmailConfirmationSuccessView,
    EmailConfirmationFailedView,
    AddressListView,
    address_create,
    address_update,
    address_delete,
    set_default_address,
    account_update,
)

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('confirm-email/<str:uidb64>/<str:token>/', confirm_email, name='confirm_email'),
    path('confirm-email/success/', EmailConfirmationSuccessView.as_view(), name='confirm_email_success'),
    path('confirm-email/failed/', EmailConfirmationFailedView.as_view(), name='confirm_email_failed'),
    path('addresses/', AddressListView.as_view(), name='address_list'),
    path('addresses/add/', address_create, name='address_create'),
    path('addresses/<int:pk>/edit/', address_update, name='address_update'),
    path('addresses/<int:pk>/delete/', address_delete, name='address_delete'),
    path('addresses/<int:pk>/set-default/', set_default_address, name='set_default_address'),
    path('update/', account_update, name='account_update'),
]
