
from .models import UserModel, UserSubscription
from .serializers import UserModelSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
from django.utils import timezone


class UserRepository:
    @staticmethod
    def get_user_by_id(institution_id):
        info = UserModel.objects.filter(id=institution_id).first()
        return info

    @staticmethod
    def create_user(data):
        serializer = UserModelSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return serializer
        return serializer.errors
       

    @staticmethod
    def update_user(user_model, data):
        for field, value in data.items():
            setattr(user_model, field, value)
        user_model.save()
        return user_model

    @staticmethod
    def delete_user(user_id):
        product = UserModel.objects.get(id=user_id)
        if product:  
            product.delete()
            return {"success": "deleted successfully"}
        return {"error": "UserModel not found"}


    def get_user_by_id(self, id):
        """Get a single user by ID."""
        try:
            return UserModel.objects.get(id=id)
        except UserModel.DoesNotExist:
            raise ValueError({"message": "User not found"})
    def get_user_by_email(email):
        """Get a single user by ID."""
        try:
            return UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            raise ValueError({"message": "Institution not found"})

    def get_user(self, **kwargs):
        """Get a single user by ID."""
        try:
            return UserModel.objects.get(**kwargs)
        except UserModel.DoesNotExist:
            raise ValueError({"message": "User not found"})

    def get_all_users(self):
        """Get all users."""
        return UserModel.objects.all()

    def update_user(self, id, validated_data):
        """Update user information."""
        user = self.get_user(id)
        user.first_name = validated_data.get("first_name", user.first_name)
        user.last_name = validated_data.get("first_name", user.last_name)
        user.company_name = validated_data.get("company_name", user.company_name)
        user.is_active = validated_data.get("is_active", user.is_active)
        user.is_verified = validated_data.get("is_verified", user.is_verified)
        user.address = validated_data.get("address", user.address)
        user.phone = validated_data.get("phone", user.phone)
        user.save()
        return user


    def change_password(self, id, old_password, new_password):
        """Change user's password."""
        user = UserModel.objects.get(id=id)
        if user.check_password(old_password):
            user.password = make_password(new_password)
            user.save()
            return user
        raise ValueError("Invalid credentials")

    def verify_email(id):
        try:
            user = UserModel.objects.get(id=id)
        except UserModel.DoesNotExist:
            raise ValueError("User not found")
        user.is_verified = True
        user.save()
        refresh = RefreshToken.for_user(user)
        refresh["id"] = user.id
        refresh["verification_code"] = None
        refresh["is_active"] = user.is_active

        return user

    def reset_password(id, new_password):
        """Forgot password."""
        try:
            user = UserModel.objects.get(id=id)
            if user:
                user.password = make_password(new_password)
                user.save()
                return user
            raise serializers.ValidationError("User not found")
        except UserModel.DoesNotExist:
            raise ValueError("User not found")
    def change_password(self, id, old_password, new_password):
        """Change user's password."""
        user = UserModel.objects.get(id=id)
        if user.check_password(old_password):
            user.password = make_password(new_password)
            user.save()
            return user
        raise serializers.ValidationError("Invalid credentials")
    



    @staticmethod
    def update_subscription(email, reference):
        """Update user subscription or create a new one."""
        try:
            user_model = UserModel.objects.get(email=email)
            data = {
                "UserModel": UserModel,
                "subscription_type": "yearly",
                "subscription_ref": reference,
                "subscribed_at": timezone.now(),
                "expired_at": timezone.now() + timedelta(days=365),
            }

            UserSubscription.objects.create(**data)

            user_model.active_subscription = True
            user_model.save(update_fields=["active_subscription"])

            return True

        except ObjectDoesNotExist:
            return None
        except Exception as e:
            print(f"Error updating subscription: {str(e)}")
            return None

    @staticmethod
    def deactivate_expired_institutions():
        """
        Finds all institutions whose subscriptions are expired or missing,
        and deactivates them (sets active_subscription = False).
        """
        try:
            users = UserModel.objects.all()

            for user_model in users:
                subscription = UserSubscription.objects.filter(
                    user_model=UserModel
                ).order_by('-expired_at').first()

                if not subscription or subscription.expired_at < datetime.now():
                    if user_model.active_subscription:
                        user_model.active_subscription = False
                        user_model.save(update_fields=["active_subscription"])
                        print(f"[DEACTIVATED] {user_model.email}")

        except Exception as e:
            print(f"[ERROR] Failed to deactivate expired institutions: {str(e)}")




