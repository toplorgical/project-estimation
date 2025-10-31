from django.db import models
from django.core.validators import MinValueValidator
from materials.models import Material
from machinery.models import Machinery


class Supplier(models.Model):
    """Supplier model for tracking material/machinery suppliers"""
    
    name = models.CharField(max_length=200, unique=True)
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # Location coverage
    locations = models.JSONField(default=list, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_scraped = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PriceData(models.Model):
    """Price data for materials and machinery"""
    
    # Content type for generic relation
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='price_data'
    )
    machinery = models.ForeignKey(
        Machinery,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='price_data'
    )
    
    # Supplier information
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='price_data'
    )
    
    # Pricing information
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    unit = models.CharField(max_length=20)
    
    # For machinery, different pricing models
    rental_price_daily = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    rental_price_weekly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Availability
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(null=True, blank=True)
    
    # Location
    location = models.CharField(max_length=200, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    
    # Source information
    source_url = models.URLField(blank=True)
    sku = models.CharField(max_length=100, blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    scraped_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['material', 'supplier', 'is_active']),
            models.Index(fields=['machinery', 'supplier', 'is_active']),
            models.Index(fields=['location', 'is_active']),
            models.Index(fields=['price', 'created_at']),
        ]
    
    def __str__(self):
        item = self.material or self.machinery
        return f"{item.name} - {self.supplier.name} - £{self.price}"
    
    def get_item(self):
        """Get the associated material or machinery"""
        return self.material or self.machinery


class PriceAlert(models.Model):
    """Price alerts for users"""
    
    ALERT_TYPES = [
        ('price_drop', 'Price Drop'),
        ('price_increase', 'Price Increase'),
        ('back_in_stock', 'Back in Stock'),
        ('out_of_stock', 'Out of Stock'),
    ]
    
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='price_alerts'
    )
    
    # Item being monitored
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='price_alerts'
    )
    machinery = models.ForeignKey(
        Machinery,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='price_alerts'
    )
    
    # Alert configuration
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    threshold_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    location = models.CharField(max_length=200, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['alert_type', 'is_active']),
        ]
    
    def __str__(self):
        item = self.material or self.machinery
        return f"Alert: {item.name} - {self.alert_type}"


class PriceHistory(models.Model):
    """Aggregated price history for analytics"""
    
    # Item being tracked
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='price_history'
    )
    machinery = models.ForeignKey(
        Machinery,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='price_history'
    )
    
    # Price statistics
    avg_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    max_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Location and time
    location = models.CharField(max_length=200, blank=True)
    date = models.DateField()
    
    # Metadata
    data_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['material', 'machinery', 'location', 'date']
        indexes = [
            models.Index(fields=['material', 'location', 'date']),
            models.Index(fields=['machinery', 'location', 'date']),
        ]
    
    def __str__(self):
        item = self.material or self.machinery
        return f"{item.name} - {self.location} - {self.date}"