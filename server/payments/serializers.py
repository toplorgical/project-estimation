from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SubscriptionPlan, UserSubscription, PaymentMethod, Invoice

User = get_user_model()


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'price', 'currency', 'interval',
            'max_projects', 'max_estimates_per_project', 'max_collaborators',
            'export_formats', 'advanced_features', 'description',
            'features_list', 'is_active'
        ]


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'plan', 'plan_name', 'plan_details', 'status',
            'current_period_start', 'current_period_end', 'cancel_at_period_end',
            'canceled_at', 'trial_start', 'trial_end', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = (
            'id', 'status', 'current_period_start', 'current_period_end',
            'canceled_at', 'trial_start', 'trial_end', 'created_at', 'updated_at'
        )


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'card_brand', 'card_last4', 'card_exp_month',
            'card_exp_year', 'is_default', 'is_active', 'created_at'
        ]
        read_only_fields = ('id', 'created_at')


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'id', 'stripe_invoice_id', 'amount_due', 'amount_paid',
            'currency', 'status', 'invoice_date', 'due_date', 'paid_at',
            'period_start', 'period_end', 'invoice_pdf', 'hosted_invoice_url',
            'created_at'
        ]
        read_only_fields = ('id', 'created_at')


class CreateSubscriptionSerializer(serializers.Serializer):
    """Serializer for creating subscriptions"""
    plan_id = serializers.IntegerField()
    payment_method_id = serializers.CharField()
    
    def validate_plan_id(self, value):
        try:
            plan = SubscriptionPlan.objects.get(id=value, is_active=True)
            return value
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive subscription plan")


class UpdateSubscriptionSerializer(serializers.Serializer):
    """Serializer for updating subscriptions"""
    plan_id = serializers.IntegerField()
    prorate = serializers.BooleanField(default=True)
    
    def validate_plan_id(self, value):
        try:
            plan = SubscriptionPlan.objects.get(id=value, is_active=True)
            return value
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive subscription plan")


class CancelSubscriptionSerializer(serializers.Serializer):
    """Serializer for canceling subscriptions"""
    cancel_at_period_end = serializers.BooleanField(default=True)
    reason = serializers.CharField(required=False, allow_blank=True)


class AddPaymentMethodSerializer(serializers.Serializer):
    """Serializer for adding payment methods"""
    payment_method_id = serializers.CharField()
    set_as_default = serializers.BooleanField(default=False)


class SubscriptionUsageSerializer(serializers.Serializer):
    """Serializer for subscription usage data"""
    projects_used = serializers.IntegerField()
    projects_limit = serializers.IntegerField()
    estimates_used = serializers.IntegerField()
    collaborators_used = serializers.IntegerField()
    collaborators_limit = serializers.IntegerField()
    features_available = serializers.ListField(child=serializers.CharField())
    billing_period_start = serializers.DateTimeField()
    billing_period_end = serializers.DateTimeField()