from django.urls import path
from . import views

urlpatterns = [
    # Subscription plans
    path('plans/', views.SubscriptionPlanListView.as_view(), name='subscription-plans'),
    
    # User subscription
    path('subscription/', views.UserSubscriptionView.as_view(), name='user-subscription'),
    path('create-subscription/', views.create_subscription, name='create-subscription'),
    path('update-subscription/', views.update_subscription, name='update-subscription'),
    path('cancel-subscription/', views.cancel_subscription, name='cancel-subscription'),
    path('subscription/usage/', views.subscription_usage, name='subscription-usage'),
    
    # Payment methods
    path('payment-methods/', views.PaymentMethodListView.as_view(), name='payment-methods'),
    path('payment-methods/add/', views.add_payment_method, name='add-payment-method'),
    
    # Invoices
    path('invoices/', views.InvoiceListView.as_view(), name='invoices'),
    
    # Webhooks
    path('webhook/', views.stripe_webhook, name='stripe-webhook'),
]