from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from .models import UserModel
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password


class UserModelSerializer(serializers.ModelSerializer):
    address = serializers.CharField(required=False)
   
    phone = serializers.CharField(required=False)
  
    active_subscription =serializers.CharField(required=False)

    class Meta:
        model = UserModel
        fields = ['id', 'first_name', 'first_name', 'active_subscription', 'email', 'address', 'phone', 'password', ]
        extra_kwargs = {
        'password': {'write_only': True},        
    }

    def validate_first_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Invalid first_name.")
        return value
    def validate_last_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Invalid last_name.")
        return value

    def validate_password(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Invalid password.")
        return value

    def validate_email(self, value):
        if UserModel.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        if "@" not in value:
            raise serializers.ValidationError("Invalid email info.")
        return value

    def create(self, validated_data):
        """
        Custom create to ensure UserModel instance is returned and password is hashed.
        """
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)
        return UserModel.objects.create(**validated_data)
    
    def update(self, instance, validated_data): 
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def change_password(user_instance, old_password, new_password):
        if not user_instance.check_password(old_password):
            raise serializers.ValidationError("Old password is incorrect.")
        
        user_instance.password = make_password(new_password)
        user_instance.save()
        return user_instance




class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def loginUser(data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = UserModel.objects.get(email=email)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({"message": "Invalid login credentials"})

        if user.check_password(password):
            return user

        raise serializers.ValidationError({"message": "Invalid login credentials"})


    def get_token(user, code=None):
        if not user:
            raise ValueError("User instance is required")

        if not hasattr(user, "id"):
            raise TypeError("Expected a User instance, got something else")

        refresh = RefreshToken.for_user(user)
        refresh["id"] = user.id
        refresh["email"] = user.email
        refresh["is_verified"] = user.is_verified

        
        if code is not None:
            refresh["verification_code"] = code
        else:
            refresh["verification_code"] = None 

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    
    
