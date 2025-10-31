from django.db import models
from django.core.validators import MinValueValidator


class MaterialCategory(models.Model):
    """Categories for materials"""
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
        verbose_name_plural = 'Material Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Material(models.Model):
    """Material model for construction materials"""
    
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('tonne', 'Tonne'),
        ('m', 'Meter'),
        ('m2', 'Square Meter'),
        ('m3', 'Cubic Meter'),
        ('piece', 'Piece'),
        ('litre', 'Litre'),
        ('bag', 'Bag'),
        ('roll', 'Roll'),
        ('sheet', 'Sheet'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        MaterialCategory,
        on_delete=models.CASCADE,
        related_name='materials'
    )
    sku = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    
    # Specifications
    brand = models.CharField(max_length=100, blank=True)
    specifications = models.JSONField(default=dict, blank=True)
    
    # Dimensions and properties
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
    
    # Status and tracking
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.unit})"
    
    def get_current_price(self, location=None):
        """Get current price for this material"""
        from pricing.models import PriceData
        
        filters = {'material': self, 'is_active': True}
        if location:
            filters['location__icontains'] = location
        
        try:
            price_data = PriceData.objects.filter(**filters).latest('created_at')
            return price_data.price
        except PriceData.DoesNotExist:
            return None
    
    def get_price_history(self, days=30):
        """Get price history for this material"""
        from pricing.models import PriceData
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        return PriceData.objects.filter(
            material=self,
            created_at__range=[start_date, end_date]
        ).order_by('-created_at')
    
    @property
    def volume(self):
        """Calculate volume if dimensions are available"""
        if self.length and self.width and self.height:
            return self.length * self.width * self.height
        return None