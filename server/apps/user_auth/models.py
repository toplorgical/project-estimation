from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from datetime import datetime



class UserModel(AbstractBaseUser, PermissionsMixin):  
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company_name = models.CharField(max_length=100)
    address = models.TextField(null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, null=True)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active_subscription = models.BooleanField(default=False)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Institution"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['id']),
        ]
    

class UserSubscription(models.Model):
    user_model = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    subscription_type = models.CharField(max_length=100)
    subscription_ref= models.CharField(max_length=100)
    subcribed_at = models.DateTimeField(auto_now_add=False)
    expired_at = models.DateTimeField(auto_now_add=False)
    updated_at = models.DateTimeField(auto_now=True)
