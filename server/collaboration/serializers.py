from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ProjectInvitation, ActivityLog, ProjectComment, ProjectNotification
from projects.models import Project

User = get_user_model()


class ProjectInvitationSerializer(serializers.ModelSerializer):
    inviter_name = serializers.CharField(source='inviter.full_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    invitee_name = serializers.CharField(source='invitee.full_name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = ProjectInvitation
        fields = [
            'id', 'project', 'project_name', 'inviter', 'inviter_name',
            'invitee_email', 'invitee', 'invitee_name', 'role', 'status',
            'message', 'is_expired', 'created_at', 'responded_at', 'expires_at'
        ]
        read_only_fields = (
            'id', 'inviter', 'token', 'status', 'responded_at', 'created_at', 'expires_at'
        )


class SendInvitationSerializer(serializers.Serializer):
    """Serializer for sending project invitations"""
    project_id = serializers.IntegerField()
    invitee_email = serializers.EmailField()
    role = serializers.ChoiceField(choices=ProjectInvitation.ROLE_CHOICES)
    message = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate_project_id(self, value):
        user = self.context['request'].user
        try:
            project = Project.objects.get(id=value)
            # Check if user is project owner or admin
            if project.owner != user:
                from projects.models import ProjectCollaborator
                collaborator = ProjectCollaborator.objects.filter(
                    project=project, user=user, role='admin'
                ).first()
                if not collaborator:
                    raise serializers.ValidationError("You don't have permission to invite collaborators")
            return value
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found")
    
    def validate(self, data):
        # Check if invitation already exists
        existing = ProjectInvitation.objects.filter(
            project_id=data['project_id'],
            invitee_email=data['invitee_email'],
            status='pending'
        ).exists()
        
        if existing:
            raise serializers.ValidationError("Invitation already sent to this email")
        
        return data


class ActivityLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'project', 'project_name', 'user', 'user_name',
            'action_type', 'description', 'estimate_id', 'material_id',
            'machinery_id', 'metadata', 'created_at'
        ]
        read_only_fields = ('id', 'created_at')


class ProjectCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    replies_count = serializers.SerializerMethodField()
    can_resolve = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectComment
        fields = [
            'id', 'project', 'user', 'user_name', 'user_email',
            'content', 'estimate', 'parent', 'is_resolved',
            'resolved_by', 'resolved_at', 'replies_count', 'can_resolve',
            'created_at', 'updated_at'
        ]
        read_only_fields = (
            'id', 'user', 'resolved_by', 'resolved_at', 'created_at', 'updated_at'
        )
    
    def get_replies_count(self, obj):
        return obj.replies.count()
    
    def get_can_resolve(self, obj):
        user = self.context['request'].user
        # Only project owner, admins, or comment author can resolve
        if obj.project.owner == user or obj.user == user:
            return True
        
        from projects.models import ProjectCollaborator
        return ProjectCollaborator.objects.filter(
            project=obj.project, user=user, role='admin'
        ).exists()
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProjectCommentReplySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = ProjectComment
        fields = [
            'id', 'user', 'user_name', 'user_email', 'content',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProjectNotificationSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = ProjectNotification
        fields = [
            'id', 'project', 'project_name', 'notification_type',
            'title', 'message', 'estimate_id', 'comment_id',
            'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ('id', 'created_at')


class InvitationResponseSerializer(serializers.Serializer):
    """Serializer for responding to invitations"""
    action = serializers.ChoiceField(choices=['accept', 'decline'])
    token = serializers.CharField()