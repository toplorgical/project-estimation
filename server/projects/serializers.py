from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project, ProjectCollaborator

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    total_estimate = serializers.DecimalField(
        source='get_total_estimate',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    collaborators_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'project_type', 'status',
            'address', 'city', 'postcode', 'country', 'location',
            'total_area', 'floors', 'owner', 'owner_name',
            'total_estimate', 'collaborators_count',
            'start_date', 'end_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')
    
    def get_collaborators_count(self, obj):
        return obj.collaborators.count()
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class ProjectDetailSerializer(ProjectSerializer):
    collaborators = serializers.SerializerMethodField()
    
    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['collaborators']
    
    def get_collaborators(self, obj):
        collaborators = ProjectCollaborator.objects.filter(project=obj).select_related('user')
        return [{
            'id': collab.user.id,
            'name': collab.user.full_name,
            'email': collab.user.email,
            'role': collab.role,
            'invited_at': collab.invited_at,
            'accepted_at': collab.accepted_at,
        } for collab in collaborators]


class ProjectCollaboratorSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = ProjectCollaborator
        fields = [
            'id', 'user', 'user_name', 'user_email', 'role',
            'invited_at', 'accepted_at'
        ]
        read_only_fields = ('id', 'invited_at', 'accepted_at')


class InviteCollaboratorSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=ProjectCollaborator.ROLE_CHOICES)
    
    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")
        return value