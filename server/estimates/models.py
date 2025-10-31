from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from projects.models import Project
from materials.models import Material
from machinery.models import Machinery

User = get_user_model()


class Estimate(models.Model):
    """Main estimate model for project cost calculations"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='estimates'
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Cost breakdown
    materials_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    labor_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    machinery_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    overhead_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Totals
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    vat_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=0.20,  # 20% VAT
        validators=[MinValueValidator(0)]
    )
    vat_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['created_by', 'status']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.project.name}"
    
    def calculate_totals(self):
        """Calculate estimate totals"""
        self.subtotal = (
            self.materials_cost +
            self.labor_cost +
            self.machinery_cost +
            self.overhead_cost
        )
        self.vat_amount = self.subtotal * self.vat_rate
        self.total_cost = self.subtotal + self.vat_amount
        self.save()
    
    def update_material_costs(self):
        """Update material costs based on current items"""
        total = sum(
            item.total_cost for item in self.material_items.all()
        )
        self.materials_cost = total
        self.calculate_totals()
    
    def update_machinery_costs(self):
        """Update machinery costs based on current items"""
        total = sum(
            item.total_cost for item in self.machinery_items.all()
        )
        self.machinery_cost = total
        self.calculate_totals()


class EstimateMaterialItem(models.Model):
    """Materials included in an estimate"""
    
    estimate = models.ForeignKey(
        Estimate,
        on_delete=models.CASCADE,
        related_name='material_items'
    )
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    
    # Quantity and pricing
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Waste factor
    waste_factor = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=0.10,  # 10% waste
        validators=[MinValueValidator(0)]
    )
    
    # Supplier information
    supplier = models.CharField(max_length=200, blank=True)
    supplier_location = models.CharField(max_length=200, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['estimate', 'material']
        indexes = [
            models.Index(fields=['estimate', 'material']),
        ]
    
    def __str__(self):
        return f"{self.material.name} - {self.quantity} {self.material.unit}"
    
    def save(self, *args, **kwargs):
        # Calculate total cost including waste
        adjusted_quantity = self.quantity * (1 + self.waste_factor)
        self.total_cost = adjusted_quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Update estimate totals
        self.estimate.update_material_costs()


class EstimateMachineryItem(models.Model):
    """Machinery included in an estimate"""
    
    RENTAL_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('purchase', 'Purchase'),
    ]
    
    estimate = models.ForeignKey(
        Estimate,
        on_delete=models.CASCADE,
        related_name='machinery_items'
    )
    machinery = models.ForeignKey(Machinery, on_delete=models.CASCADE)
    
    # Rental information
    rental_type = models.CharField(max_length=20, choices=RENTAL_TYPES)
    duration = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Additional costs
    transport_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    setup_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Total cost
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Supplier information
    supplier = models.CharField(max_length=200, blank=True)
    supplier_location = models.CharField(max_length=200, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['estimate', 'machinery']
        indexes = [
            models.Index(fields=['estimate', 'machinery']),
        ]
    
    def __str__(self):
        return f"{self.machinery.name} - {self.duration} {self.rental_type}"
    
    def save(self, *args, **kwargs):
        # Calculate total cost
        rental_cost = self.duration * self.unit_price
        self.total_cost = rental_cost + self.transport_cost + self.setup_cost
        super().save(*args, **kwargs)
        
        # Update estimate totals
        self.estimate.update_machinery_costs()


class EstimateSubstitution(models.Model):
    """Alternative material/machinery suggestions"""
    
    SUBSTITUTION_TYPES = [
        ('material', 'Material'),
        ('machinery', 'Machinery'),
    ]
    
    estimate = models.ForeignKey(
        Estimate,
        on_delete=models.CASCADE,
        related_name='substitutions'
    )
    
    # Original item
    original_material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='original_substitutions'
    )
    original_machinery = models.ForeignKey(
        Machinery,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='original_substitutions'
    )
    
    # Alternative item
    alternative_material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alternative_substitutions'
    )
    alternative_machinery = models.ForeignKey(
        Machinery,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alternative_substitutions'
    )
    
    # Comparison data
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    alternative_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    cost_savings = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # Recommendation data
    reason = models.TextField()
    confidence_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MinValueValidator(1)]
    )
    
    # Status
    is_applied = models.BooleanField(default=False)
    applied_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['estimate', 'is_applied']),
        ]
    
    def __str__(self):
        original = self.original_material or self.original_machinery
        alternative = self.alternative_material or self.alternative_machinery
        return f"Substitute {original.name} with {alternative.name}"
    
    def save(self, *args, **kwargs):
        # Calculate cost savings
        self.cost_savings = self.original_price - self.alternative_price
        super().save(*args, **kwargs)