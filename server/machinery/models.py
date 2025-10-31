from django.db import models
from django.core.validators import MinValueValidator


class MachineryCategory(models.Model):
    """Categories for machinery"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Machinery Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Machinery(models.Model):
    """Machinery model for construction equipment"""
    
    FUEL_TYPES = [
        ('diesel', 'Diesel'),
        ('petrol', 'Petrol'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('manual', 'Manual'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        MachineryCategory,
        on_delete=models.CASCADE,
        related_name='machinery'
    )
    
    # Basic information
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    
    # Technical specifications
    specifications = models.JSONField(default=dict, blank=True)
    power = models.CharField(max_length=50, blank=True)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES, blank=True)
    
    # Dimensions
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Capacity and performance
    capacity = models.CharField(max_length=100, blank=True)
    max_load = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Machinery'
        ordering = ['name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['fuel_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.brand} {self.model}"
    
    def get_current_rental_price(self, location=None, rental_type='daily'):
        """Get current rental price for this machinery"""
        from pricing.models import PriceData
        
        filters = {'machinery': self, 'is_active': True}
        if location:
            filters['location__icontains'] = location
        
        try:
            price_data = PriceData.objects.filter(**filters).latest('created_at')
            
            if rental_type == 'daily':
                return price_data.rental_price_daily
            elif rental_type == 'weekly':
                return price_data.rental_price_weekly
            else:
                return price_data.price
        except PriceData.DoesNotExist:
            return None
    
    def get_purchase_price(self, location=None):
        """Get current purchase price for this machinery"""
        from pricing.models import PriceData
        
        filters = {'machinery': self, 'is_active': True}
        if location:
            filters['location__icontains'] = location
        
        try:
            price_data = PriceData.objects.filter(**filters).latest('created_at')
            return price_data.price
        except PriceData.DoesNotExist:
            return None
    
    def get_availability(self, location=None):
        """Check availability in specified location"""
        from pricing.models import PriceData
        
        filters = {'machinery': self, 'is_active': True, 'in_stock': True}
        if location:
            filters['location__icontains'] = location
        
        return PriceData.objects.filter(**filters).exists()