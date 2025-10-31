from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from .models import (
    SubscriptionPlan, UserSubscription, PaymentMethod, Invoice, WebhookEvent
)
from .serializers import (
    SubscriptionPlanSerializer,
    UserSubscriptionSerializer,
    PaymentMethodSerializer,
    InvoiceSerializer,
    CreateSubscriptionSerializer,
    UpdateSubscriptionSerializer,
    CancelSubscriptionSerializer,
    AddPaymentMethodSerializer,
    SubscriptionUsageSerializer
)
import stripe
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

# Set Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY


class SubscriptionPlanListView(generics.ListAPIView):
    """List available subscription plans"""
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class UserSubscriptionView(generics.RetrieveAPIView):
    """Get user's current subscription"""
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        try:
            return self.request.user.subscription
        except UserSubscription.DoesNotExist:
            return None
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response({'subscription': None})
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_subscription(request):
    """Create a new subscription"""
    serializer = CreateSubscriptionSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    user = request.user
    
    try:
        # Get subscription plan
        plan = SubscriptionPlan.objects.get(id=data['plan_id'])
        
        # Create or get Stripe customer
        if user.stripe_customer_id:
            customer = stripe.Customer.retrieve(user.stripe_customer_id)
        else:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={'user_id': user.id}
            )
            user.stripe_customer_id = customer.id
            user.save()
        
        # Attach payment method to customer
        stripe.PaymentMethod.attach(
            data['payment_method_id'],
            customer=customer.id
        )
        
        # Set as default payment method
        stripe.Customer.modify(
            customer.id,
            invoice_settings={'default_payment_method': data['payment_method_id']}
        )
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'price': plan.stripe_price_id}],
            default_payment_method=data['payment_method_id'],
            expand=['latest_invoice.payment_intent']
        )
        
        # Save subscription to database
        user_subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            stripe_subscription_id=subscription.id,
            stripe_customer_id=customer.id,
            status=subscription.status,
            current_period_start=timezone.datetime.fromtimestamp(
                subscription.current_period_start, tz=timezone.utc
            ),
            current_period_end=timezone.datetime.fromtimestamp(
                subscription.current_period_end, tz=timezone.utc
            )
        )
        
        # Save payment method
        payment_method = stripe.PaymentMethod.retrieve(data['payment_method_id'])
        PaymentMethod.objects.create(
            user=user,
            stripe_payment_method_id=payment_method.id,
            card_brand=payment_method.card.brand,
            card_last4=payment_method.card.last4,
            card_exp_month=payment_method.card.exp_month,
            card_exp_year=payment_method.card.exp_year,
            is_default=True
        )
        
        # Update user subscription plan
        user.subscription_plan = plan.name.lower()
        user.save()
        
        return Response({
            'subscription': UserSubscriptionSerializer(user_subscription).data,
            'client_secret': subscription.latest_invoice.payment_intent.client_secret
        }, status=status.HTTP_201_CREATED)
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating subscription: {str(e)}")
        return Response(
            {'error': f'Payment error: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        return Response(
            {'error': f'Failed to create subscription: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_subscription(request):
    """Update user's subscription plan"""
    try:
        user_subscription = request.user.subscription
    except UserSubscription.DoesNotExist:
        return Response(
            {'error': 'No active subscription found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = UpdateSubscriptionSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        # Get new plan
        new_plan = SubscriptionPlan.objects.get(id=data['plan_id'])
        
        # Update Stripe subscription
        subscription = stripe.Subscription.modify(
            user_subscription.stripe_subscription_id,
            items=[{
                'id': stripe.Subscription.retrieve(
                    user_subscription.stripe_subscription_id
                ).items.data[0].id,
                'price': new_plan.stripe_price_id,
            }],
            proration_behavior='create_prorations' if data['prorate'] else 'none'
        )
        
        # Update database
        user_subscription.plan = new_plan
        user_subscription.status = subscription.status
        user_subscription.current_period_start = timezone.datetime.fromtimestamp(
            subscription.current_period_start, tz=timezone.utc
        )
        user_subscription.current_period_end = timezone.datetime.fromtimestamp(
            subscription.current_period_end, tz=timezone.utc
        )
        user_subscription.save()
        
        # Update user subscription plan
        request.user.subscription_plan = new_plan.name.lower()
        request.user.save()
        
        return Response(
            UserSubscriptionSerializer(user_subscription).data
        )
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error updating subscription: {str(e)}")
        return Response(
            {'error': f'Payment error: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        logger.error(f"Error updating subscription: {str(e)}")
        return Response(
            {'error': f'Failed to update subscription: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_subscription(request):
    """Cancel user's subscription"""
    try:
        user_subscription = request.user.subscription
    except UserSubscription.DoesNotExist:
        return Response(
            {'error': 'No active subscription found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = CancelSubscriptionSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        if data['cancel_at_period_end']:
            # Cancel at period end
            subscription = stripe.Subscription.modify(
                user_subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
            user_subscription.cancel_at_period_end = True
            message = 'Subscription will be canceled at the end of the current billing period'
        else:
            # Cancel immediately
            subscription = stripe.Subscription.delete(
                user_subscription.stripe_subscription_id
            )
            user_subscription.status = 'canceled'
            user_subscription.canceled_at = timezone.now()
            message = 'Subscription canceled immediately'
        
        user_subscription.save()
        
        return Response({'message': message})
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error canceling subscription: {str(e)}")
        return Response(
            {'error': f'Payment error: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        logger.error(f"Error canceling subscription: {str(e)}")
        return Response(
            {'error': f'Failed to cancel subscription: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class PaymentMethodListView(generics.ListAPIView):
    """List user's payment methods"""
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(
            user=self.request.user,
            is_active=True
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_payment_method(request):
    """Add a new payment method"""
    serializer = AddPaymentMethodSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    user = request.user
    
    try:
        # Ensure user has a Stripe customer ID
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={'user_id': user.id}
            )
            user.stripe_customer_id = customer.id
            user.save()
        
        # Attach payment method to customer
        stripe.PaymentMethod.attach(
            data['payment_method_id'],
            customer=user.stripe_customer_id
        )
        
        # Get payment method details
        payment_method = stripe.PaymentMethod.retrieve(data['payment_method_id'])
        
        # Set as default if requested
        if data['set_as_default']:
            # Remove default from other payment methods
            PaymentMethod.objects.filter(user=user).update(is_default=False)
            
            # Set as default in Stripe
            stripe.Customer.modify(
                user.stripe_customer_id,
                invoice_settings={'default_payment_method': data['payment_method_id']}
            )
        
        # Save to database
        payment_method_obj = PaymentMethod.objects.create(
            user=user,
            stripe_payment_method_id=payment_method.id,
            card_brand=payment_method.card.brand,
            card_last4=payment_method.card.last4,
            card_exp_month=payment_method.card.exp_month,
            card_exp_year=payment_method.card.exp_year,
            is_default=data['set_as_default']
        )
        
        return Response(
            PaymentMethodSerializer(payment_method_obj).data,
            status=status.HTTP_201_CREATED
        )
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error adding payment method: {str(e)}")
        return Response(
            {'error': f'Payment error: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        logger.error(f"Error adding payment method: {str(e)}")
        return Response(
            {'error': f'Failed to add payment method: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class InvoiceListView(generics.ListAPIView):
    """List user's invoices"""
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def subscription_usage(request):
    """Get subscription usage information"""
    user = request.user
    
    try:
        subscription = user.subscription
        
        # Count current usage
        projects_used = user.owned_projects.filter(status__in=['draft', 'active']).count()
        
        # Get collaborators count across all projects
        collaborators_used = 0
        for project in user.owned_projects.all():
            collaborators_used += project.collaborators.count()
        
        # Estimate count (example - you might want to count differently)
        estimates_used = sum(
            project.estimates.count() for project in user.owned_projects.all()
        )
        
        usage_data = {
            'projects_used': projects_used,
            'projects_limit': subscription.plan.max_projects,
            'estimates_used': estimates_used,
            'collaborators_used': collaborators_used,
            'collaborators_limit': subscription.plan.max_collaborators,
            'features_available': subscription.plan.advanced_features,
            'billing_period_start': subscription.current_period_start,
            'billing_period_end': subscription.current_period_end,
        }
        
        serializer = SubscriptionUsageSerializer(usage_data)
        return Response(serializer.data)
    
    except UserSubscription.DoesNotExist:
        return Response(
            {'error': 'No active subscription found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Invalid payload in Stripe webhook")
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature in Stripe webhook")
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # Store webhook event
    webhook_event, created = WebhookEvent.objects.get_or_create(
        stripe_event_id=event['id'],
        defaults={
            'event_type': event['type'],
            'data': event['data']
        }
    )
    
    if not created and webhook_event.processed:
        return Response({'status': 'already processed'})
    
    # Process webhook
    try:
        if event['type'] == 'customer.subscription.updated':
            handle_subscription_updated(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            handle_subscription_deleted(event['data']['object'])
        elif event['type'] == 'invoice.payment_succeeded':
            handle_invoice_payment_succeeded(event['data']['object'])
        elif event['type'] == 'invoice.payment_failed':
            handle_invoice_payment_failed(event['data']['object'])
        
        webhook_event.processed = True
        webhook_event.processed_at = timezone.now()
        webhook_event.save()
        
    except Exception as e:
        logger.error(f"Error processing webhook {event['id']}: {str(e)}")
        webhook_event.error_message = str(e)
        webhook_event.save()
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({'status': 'success'})


def handle_subscription_updated(subscription_data):
    """Handle subscription updated webhook"""
    try:
        user_subscription = UserSubscription.objects.get(
            stripe_subscription_id=subscription_data['id']
        )
        
        user_subscription.status = subscription_data['status']
        user_subscription.current_period_start = timezone.datetime.fromtimestamp(
            subscription_data['current_period_start'], tz=timezone.utc
        )
        user_subscription.current_period_end = timezone.datetime.fromtimestamp(
            subscription_data['current_period_end'], tz=timezone.utc
        )
        user_subscription.cancel_at_period_end = subscription_data.get('cancel_at_period_end', False)
        
        if subscription_data.get('canceled_at'):
            user_subscription.canceled_at = timezone.datetime.fromtimestamp(
                subscription_data['canceled_at'], tz=timezone.utc
            )
        
        user_subscription.save()
        
        logger.info(f"Updated subscription {subscription_data['id']}")
        
    except UserSubscription.DoesNotExist:
        logger.error(f"Subscription {subscription_data['id']} not found in database")


def handle_subscription_deleted(subscription_data):
    """Handle subscription deleted webhook"""
    try:
        user_subscription = UserSubscription.objects.get(
            stripe_subscription_id=subscription_data['id']
        )
        
        user_subscription.status = 'canceled'
        user_subscription.canceled_at = timezone.now()
        user_subscription.save()
        
        # Update user subscription plan to free
        user_subscription.user.subscription_plan = 'free'
        user_subscription.user.save()
        
        logger.info(f"Canceled subscription {subscription_data['id']}")
        
    except UserSubscription.DoesNotExist:
        logger.error(f"Subscription {subscription_data['id']} not found in database")


def handle_invoice_payment_succeeded(invoice_data):
    """Handle successful invoice payment"""
    try:
        user_subscription = UserSubscription.objects.get(
            stripe_subscription_id=invoice_data['subscription']
        )
        
        # Create or update invoice record
        Invoice.objects.update_or_create(
            stripe_invoice_id=invoice_data['id'],
            defaults={
                'user': user_subscription.user,
                'subscription': user_subscription,
                'amount_due': invoice_data['amount_due'] / 100,  # Convert from cents
                'amount_paid': invoice_data['amount_paid'] / 100,
                'currency': invoice_data['currency'].upper(),
                'status': invoice_data['status'],
                'invoice_date': timezone.datetime.fromtimestamp(
                    invoice_data['created'], tz=timezone.utc
                ),
                'paid_at': timezone.datetime.fromtimestamp(
                    invoice_data['status_transitions']['paid_at'], tz=timezone.utc
                ) if invoice_data['status_transitions'].get('paid_at') else None,
                'period_start': timezone.datetime.fromtimestamp(
                    invoice_data['period_start'], tz=timezone.utc
                ),
                'period_end': timezone.datetime.fromtimestamp(
                    invoice_data['period_end'], tz=timezone.utc
                ),
                'invoice_pdf': invoice_data.get('invoice_pdf', ''),
                'hosted_invoice_url': invoice_data.get('hosted_invoice_url', ''),
            }
        )
        
        logger.info(f"Payment succeeded for invoice {invoice_data['id']}")
        
    except UserSubscription.DoesNotExist:
        logger.error(f"Subscription for invoice {invoice_data['id']} not found")


def handle_invoice_payment_failed(invoice_data):
    """Handle failed invoice payment"""
    try:
        user_subscription = UserSubscription.objects.get(
            stripe_subscription_id=invoice_data['subscription']
        )
        
        # Update subscription status
        user_subscription.status = 'past_due'
        user_subscription.save()
        
        logger.info(f"Payment failed for invoice {invoice_data['id']}")
        
        # TODO: Send notification to user about failed payment
        
    except UserSubscription.DoesNotExist:
        logger.error(f"Subscription for invoice {invoice_data['id']} not found")