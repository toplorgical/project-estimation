from django.db import models
from django.db.models import JSONField
from ..user_auth.models import UserModel
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator







class Project(models.Model):
    STATUS_CHOICES = [
        ('completed', 'completed'),
        ('pending', 'Pending'),
        
    ]
    user_model = models.ForeignKey(
    UserModel,
    on_delete=models.CASCADE,
    related_name='projects'  
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    report_name = models.CharField(max_length=255)
    project_type =models.CharField(max_length=255)
    project_location=models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   



class ProjectResources(models.Model):

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_resources')
    user_model = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='project_resources')
    resource_type = models.CharField(max_length=100)
    resource_name= models.CharField(max_length=100)
    quantity= models.CharField(max_length=100)

    unit_cost= models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)   
    class Meta:
        verbose_name_plural = "project_resources"
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['user_model']),
        ]


class ProjectLabour(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_labour')
    user_model = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='project_labour')
    number_of_skills_worker = models.CharField(max_length=100)
    number_of_unskills_worker= models.CharField(max_length=100)
    project_duration= models.CharField(max_length=100)

    project_size= models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)   
    class Meta:
        verbose_name_plural = "project_labour"
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['user_model']),
        ]