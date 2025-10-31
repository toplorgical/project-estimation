from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Project(models.Model):
    """Project model for construction projects"""
    
    PROJECT_TYPES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('infrastructure', 'Infrastructure'),
        ('renovation', 'Renovation'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Location details
    address = models.TextField()
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    country = models.CharField(max_length=50, default='United Kingdom')
    
    # Project dimensions
    total_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Total area in square meters"
    )
    floors = models.PositiveIntegerField(default=1)
    
    # Ownership and collaboration
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    collaborators = models.ManyToManyField(
        User,
        through='ProjectCollaborator',
        related_name='collaborated_projects',
        blank=True
    )
    
    # Timestamps
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['project_type', 'city']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.project_type})"
    
    @property
    def location(self):
        return f"{self.city}, {self.postcode}"
    
    def get_total_estimate(self):
        """Calculate total project estimate"""
        from estimates.models import Estimate
        try:
            latest_estimate = self.estimates.latest('created_at')
            return latest_estimate.total_cost
        except Estimate.DoesNotExist:
            return 0


class ProjectCollaborator(models.Model):
    """Through model for project collaboration"""
    
    ROLE_CHOICES = [
        ('viewer', 'Viewer'),
        ('editor', 'Editor'),
        ('admin', 'Admin'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    invited_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['project', 'user']
        indexes = [
            models.Index(fields=['project', 'role']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.project.name} ({self.role})"