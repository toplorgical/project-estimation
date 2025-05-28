from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet, paystack_webhook, PaystackInitView
from django.urls import path

router = DefaultRouter()
router.register(r'account', AuthViewSet, basename='account')
router.register(r'auth', UserViewSet, basename='auth')

urlpatterns = router.urls + [
    path('auth/subscription/init/', PaystackInitView.as_view(), name='subscription-init'),
    path('paystack/webhook/', paystack_webhook, name='paystack-webhook'),
]
