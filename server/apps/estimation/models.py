# models.py
from django.db import models
from django.db.models import JSONField
from ..user_auth.models import UserModel
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class Sector(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Project(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
    ]
    
    ESTIMATION_METHOD_CHOICES = [
        ('ml', 'Machine Learning'),
        ('scraping', 'Web Scraping'),
        ('manual', 'Manual Input'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_model = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='projects'  
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    report_name = models.CharField(max_length=255)
    project_type = models.CharField(max_length=255)
    project_location = models.CharField(max_length=255)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estimation_method = models.CharField(max_length=20, choices=ESTIMATION_METHOD_CHOICES, null=True, blank=True)
    estimation_confidence = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    estimation_metadata = JSONField(null=True, blank=True)  # Stores additional estimation data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.report_name} - {self.get_status_display()}"

class ResourceCategory(models.Model):
    name = models.CharField(max_length=100)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='resource_categories')
    unit = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.name} ({self.sector.name})"

class ProjectResources(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_resources')
    user_model = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='project_resources')
    resource_category = models.ForeignKey(ResourceCategory, on_delete=models.SET_NULL, null=True, blank=True)
    resource_type = models.CharField(max_length=100)
    resource_name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    current_market_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_source = models.CharField(max_length=255, null=True, blank=True)
    price_last_updated = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_cost(self):
        return self.quantity * (self.current_market_price or self.unit_cost)
    
    class Meta:
        verbose_name_plural = "project_resources"
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['user_model']),
            models.Index(fields=['resource_category']),
        ]

class ProjectLabour(models.Model):
    LABOUR_TYPES = [
        ('skilled', 'Skilled Worker'),
        ('unskilled', 'Unskilled Worker'),
        ('supervisor', 'Supervisor/Manager'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_labour')
    user_model = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='project_labour')
    labour_type = models.CharField(max_length=20, choices=LABOUR_TYPES)
    quantity = models.PositiveIntegerField()
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    current_market_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rate_source = models.CharField(max_length=255, null=True, blank=True)
    rate_last_updated = models.DateTimeField(null=True, blank=True)
    days_required = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_cost(self):
        rate = self.current_market_rate or self.daily_rate
        return self.quantity * rate * self.days_required
    
    class Meta:
        verbose_name_plural = "project_labour"
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['user_model']),
        ]