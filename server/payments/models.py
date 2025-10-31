from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
import stripe

User = get_user_model()

# Set Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY


class SubscriptionPlan(models.Model):
    """Subscription plans available"""
    
    name = models.CharField(max_length=50, unique=True)
    stripe_price_id = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GBP')
    interval = models.CharField(max_length=20)  # month, year
    
    # Features
    max_projects = models.IntegerField()
    max_estimates_per_project = models.IntegerField()
    max_collaborators = models.IntegerField()
    export_formats = models.JSONField(default=list)  # ['pdf', 'excel']
    advanced_features = models.JSONField(default=list)  # ['substitutions', 'price_alerts']
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    description = models.TextField(blank=True)
    features_list = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - £{self.price}/{self.interval}"


class UserSubscription(models.Model):
    """User subscription details"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('past_due', 'Past Due'),
        ('unpaid', 'Unpaid'),
        ('incomplete', 'Incomplete'),
        ('incomplete_expired', 'Incomplete Expired'),
        ('trialing', 'Trialing'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )
    
    # Stripe details
    stripe_subscription_id = models.CharField(max_length=100, unique=True)
    stripe_customer_id = models.CharField(max_length=100)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Billing
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    
    # Trial
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['stripe_subscription_id']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name} ({self.status})"
    
    @property
    def is_active(self):
        return self.status in ['active', 'trialing']
    
    def can_create_projects(self):
        """Check if user can create more projects"""
        if not self.is_active:
            return False
        
        current_projects = self.user.owned_projects.filter(status__in=['draft', 'active']).count()
        return current_projects < self.plan.max_projects
    
    def can_add_collaborators(self, project):
        """Check if user can add more collaborators to a project"""
        if not self.is_active:
            return False
        
        current_collaborators = project.collaborators.count()
        return current_collaborators < self.plan.max_collaborators
    
    def has_feature(self, feature):
        """Check if subscription includes a specific feature"""
        return feature in self.plan.advanced_features


class PaymentMethod(models.Model):
    """User payment methods"""
    
    CARD_BRANDS = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
        ('discover', 'Discover'),
        ('diners', 'Diners Club'),
        ('jcb', 'JCB'),
        ('unionpay', 'UnionPay'),
        ('unknown', 'Unknown'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    
    # Stripe details
    stripe_payment_method_id = models.CharField(max_length=100, unique=True)
    
    # Card details
    card_brand = models.CharField(max_length=20, choices=CARD_BRANDS)
    card_last4 = models.CharField(max_length=4)
    card_exp_month = models.IntegerField()
    card_exp_year = models.IntegerField()
    
    # Status
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_default']),
        ]
    
    def __str__(self):
        return f"{self.card_brand.title()} ****{self.card_last4}"


class Invoice(models.Model):
    """Invoice records from Stripe"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('uncollectible', 'Uncollectible'),
        ('void', 'Void'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    subscription = models.ForeignKey(
        UserSubscription,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    
    # Stripe details
    stripe_invoice_id = models.CharField(max_length=100, unique=True)
    
    # Invoice details
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GBP')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Dates
    invoice_date = models.DateTimeField()
    due_date = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # URLs
    invoice_pdf = models.URLField(blank=True)
    hosted_invoice_url = models.URLField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-invoice_date']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['subscription', 'invoice_date']),
        ]
    
    def __str__(self):
        return f"Invoice {self.stripe_invoice_id} - £{self.amount_due}"


class UsageRecord(models.Model):
    """Track usage for billing purposes"""
    
    USAGE_TYPES = [
        ('project_created', 'Project Created'),
        ('estimate_generated', 'Estimate Generated'),
        ('export_generated', 'Export Generated'),
        ('api_call', 'API Call'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='usage_records'
    )
    subscription = models.ForeignKey(
        UserSubscription,
        on_delete=models.CASCADE,
        related_name='usage_records'
    )
    
    usage_type = models.CharField(max_length=30, choices=USAGE_TYPES)
    quantity = models.PositiveIntegerField(default=1)
    
    # Optional references
    project_id = models.PositiveIntegerField(null=True, blank=True)
    estimate_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'usage_type', 'created_at']),
            models.Index(fields=['subscription', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.usage_type} - {self.quantity}"


class WebhookEvent(models.Model):
    """Track Stripe webhook events"""
    
    stripe_event_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=50)
    processed = models.BooleanField(default=False)
    
    # Event data
    data = models.JSONField()
    
    # Processing
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'processed']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.stripe_event_id}"