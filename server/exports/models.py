from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project
from estimates.models import Estimate

User = get_user_model()


class ExportJob(models.Model):
    """Track export jobs and their status"""
    
    EXPORT_TYPES = [
        ('project_pdf', 'Project PDF'),
        ('estimate_pdf', 'Estimate PDF'),
        ('estimate_excel', 'Estimate Excel'),
        ('materials_excel', 'Materials Excel'),
        ('project_summary', 'Project Summary'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_jobs')
    export_type = models.CharField(max_length=20, choices=EXPORT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Related objects
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='export_jobs'
    )
    estimate = models.ForeignKey(
        Estimate,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='export_jobs'
    )
    
    # Export configuration
    options = models.JSONField(default=dict, blank=True)
    
    # File information
    file_name = models.CharField(max_length=255, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    
    # Status information
    error_message = models.TextField(blank=True)
    progress = models.PositiveIntegerField(default=0)  # 0-100
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['export_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.export_type} - {self.status} - {self.user.email}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False