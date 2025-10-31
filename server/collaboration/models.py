from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project

User = get_user_model()


class ProjectInvitation(models.Model):
    """Project collaboration invitations"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    ROLE_CHOICES = [
        ('viewer', 'Viewer'),
        ('editor', 'Editor'),
        ('admin', 'Admin'),
    ]
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    inviter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_invitations'
    )
    invitee_email = models.EmailField()
    invitee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='received_invitations'
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Invitation details
    message = models.TextField(blank=True)
    token = models.CharField(max_length=100, unique=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        unique_together = ['project', 'invitee_email']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['invitee_email', 'status']),
        ]
    
    def __str__(self):
        return f"Invitation to {self.invitee_email} for {self.project.name}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at


class ActivityLog(models.Model):
    """Log of project activities for collaboration tracking"""
    
    ACTION_TYPES = [
        ('project_created', 'Project Created'),
        ('project_updated', 'Project Updated'),
        ('estimate_created', 'Estimate Created'),
        ('estimate_updated', 'Estimate Updated'),
        ('material_added', 'Material Added'),
        ('machinery_added', 'Machinery Added'),
        ('collaborator_added', 'Collaborator Added'),
        ('collaborator_removed', 'Collaborator Removed'),
        ('export_generated', 'Export Generated'),
        ('comment_added', 'Comment Added'),
    ]
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    description = models.TextField()
    
    # Optional references to related objects
    estimate_id = models.PositiveIntegerField(null=True, blank=True)
    material_id = models.PositiveIntegerField(null=True, blank=True)
    machinery_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.action_type} - {self.project.name}"


class ProjectComment(models.Model):
    """Comments on projects for collaboration"""
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_comments'
    )
    
    content = models.TextField()
    
    # Optional reference to specific estimate
    estimate = models.ForeignKey(
        'estimates.Estimate',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comments'
    )
    
    # Reply functionality
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_comments'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'created_at']),
            models.Index(fields=['estimate', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.user.full_name} on {self.project.name}"


class ProjectNotification(models.Model):
    """Notifications for project collaborators"""
    
    NOTIFICATION_TYPES = [
        ('invitation', 'Project Invitation'),
        ('project_update', 'Project Updated'),
        ('estimate_update', 'Estimate Updated'),
        ('comment_added', 'New Comment'),
        ('comment_reply', 'Comment Reply'),
        ('export_ready', 'Export Ready'),
        ('price_alert', 'Price Alert'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_notifications'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Optional references
    estimate_id = models.PositiveIntegerField(null=True, blank=True)
    comment_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
            models.Index(fields=['project', 'created_at']),
        ]
    
    def __str__(self):
        return f"Notification for {self.user.full_name}: {self.title}"