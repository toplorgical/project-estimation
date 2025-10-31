from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import ProjectInvitation, ActivityLog, ProjectComment, ProjectNotification
from .serializers import (
    ProjectInvitationSerializer,
    SendInvitationSerializer,
    ActivityLogSerializer,
    ProjectCommentSerializer,
    ProjectCommentReplySerializer,
    ProjectNotificationSerializer,
    InvitationResponseSerializer
)
from projects.models import Project, ProjectCollaborator
import uuid
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class ProjectInvitationListView(generics.ListAPIView):
    """List user's project invitations"""
    serializer_class = ProjectInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return ProjectInvitation.objects.filter(
            Q(inviter=user) | Q(invitee_email=user.email)
        ).select_related('project', 'inviter', 'invitee')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_invitation(request):
    """Send project collaboration invitation"""
    serializer = SendInvitationSerializer(data=request.data, context={'request': request})
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        project = Project.objects.get(id=data['project_id'])
        
        # Check if user is already registered
        invitee = None
        try:
            invitee = User.objects.get(email=data['invitee_email'])
        except User.DoesNotExist:
            pass
        
        # Create invitation
        invitation = ProjectInvitation.objects.create(
            project=project,
            inviter=request.user,
            invitee_email=data['invitee_email'],
            invitee=invitee,
            role=data['role'],
            message=data.get('message', ''),
            token=str(uuid.uuid4()),
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        # Send email notification (implement email service)
        send_invitation_email.delay(invitation.id)
        
        # Log activity
        ActivityLog.objects.create(
            project=project,
            user=request.user,
            action_type='collaborator_added',
            description=f"Invited {data['invitee_email']} as {data['role']}"
        )
        
        return Response(
            ProjectInvitationSerializer(invitation).data,
            status=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        logger.error(f"Error sending invitation: {str(e)}")
        return Response(
            {'error': f'Failed to send invitation: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def respond_to_invitation(request):
    """Accept or decline project invitation"""
    serializer = InvitationResponseSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        invitation = ProjectInvitation.objects.get(
            token=data['token'],
            invitee_email=request.user.email,
            status='pending'
        )
        
        if invitation.is_expired:
            return Response(
                {'error': 'Invitation has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if data['action'] == 'accept':
            # Create collaboration
            ProjectCollaborator.objects.get_or_create(
                project=invitation.project,
                user=request.user,
                defaults={'role': invitation.role}
            )
            
            invitation.status = 'accepted'
            invitation.invitee = request.user
            
            # Log activity
            ActivityLog.objects.create(
                project=invitation.project,
                user=request.user,
                action_type='collaborator_added',
                description=f"{request.user.full_name} joined as {invitation.role}"
            )
            
            message = 'Invitation accepted successfully'
        
        else:  # decline
            invitation.status = 'declined'
            message = 'Invitation declined'
        
        invitation.responded_at = timezone.now()
        invitation.save()
        
        return Response({'message': message})
    
    except ProjectInvitation.DoesNotExist:
        return Response(
            {'error': 'Invalid or expired invitation'},
            status=status.HTTP_404_NOT_FOUND
        )


class ActivityLogListView(generics.ListAPIView):
    """List project activity logs"""
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id)
        
        # Check permissions
        user = self.request.user
        if not (project.owner == user or project.collaborators.filter(id=user.id).exists()):
            return ActivityLog.objects.none()
        
        return ActivityLog.objects.filter(project=project).select_related('user')


class ProjectCommentListCreateView(generics.ListCreateAPIView):
    """List and create project comments"""
    serializer_class = ProjectCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id)
        
        # Check permissions
        user = self.request.user
        if not (project.owner == user or project.collaborators.filter(id=user.id).exists()):
            return ProjectComment.objects.none()
        
        # Filter by estimate if specified
        estimate_id = self.request.query_params.get('estimate_id')
        queryset = ProjectComment.objects.filter(project=project, parent=None)
        
        if estimate_id:
            queryset = queryset.filter(estimate_id=estimate_id)
        
        return queryset.select_related('user', 'resolved_by').prefetch_related('replies')
    
    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id)
        
        # Check permissions
        user = self.request.user
        if not (project.owner == user or project.collaborators.filter(id=user.id).exists()):
            raise PermissionError("You don't have permission to comment on this project")
        
        comment = serializer.save(project=project)
        
        # Log activity
        ActivityLog.objects.create(
            project=project,
            user=user,
            action_type='comment_added',
            description=f"Added comment: {comment.content[:50]}..."
        )
        
        # Create notifications for other collaborators
        create_comment_notifications.delay(comment.id)


class ProjectCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a comment"""
    serializer_class = ProjectCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id)
        
        # Check permissions
        user = self.request.user
        if not (project.owner == user or project.collaborators.filter(id=user.id).exists()):
            return ProjectComment.objects.none()
        
        return ProjectComment.objects.filter(project=project)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_comment_reply(request, project_id, comment_id):
    """Add reply to a comment"""
    project = get_object_or_404(Project, id=project_id)
    parent_comment = get_object_or_404(ProjectComment, id=comment_id, project=project)
    
    # Check permissions
    user = request.user
    if not (project.owner == user or project.collaborators.filter(id=user.id).exists()):
        return Response(
            {'error': 'You do not have permission to reply to this comment'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = ProjectCommentReplySerializer(data=request.data, context={'request': request})
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    reply = serializer.save(
        project=project,
        parent=parent_comment,
        estimate=parent_comment.estimate
    )
    
    # Log activity
    ActivityLog.objects.create(
        project=project,
        user=user,
        action_type='comment_added',
        description=f"Replied to comment: {reply.content[:50]}..."
    )
    
    return Response(
        ProjectCommentReplySerializer(reply).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def resolve_comment(request, project_id, comment_id):
    """Resolve a comment"""
    project = get_object_or_404(Project, id=project_id)
    comment = get_object_or_404(ProjectComment, id=comment_id, project=project)
    
    # Check permissions
    user = request.user
    can_resolve = (
        project.owner == user or
        comment.user == user or
        ProjectCollaborator.objects.filter(project=project, user=user, role='admin').exists()
    )
    
    if not can_resolve:
        return Response(
            {'error': 'You do not have permission to resolve this comment'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    comment.is_resolved = True
    comment.resolved_by = user
    comment.resolved_at = timezone.now()
    comment.save()
    
    return Response({'message': 'Comment resolved successfully'})


class ProjectNotificationListView(generics.ListAPIView):
    """List user's project notifications"""
    serializer_class = ProjectNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ProjectNotification.objects.filter(
            user=self.request.user
        ).select_related('project')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(
        ProjectNotification,
        id=notification_id,
        user=request.user
    )
    
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()
    
    return Response({'message': 'Notification marked as read'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    ProjectNotification.objects.filter(
        user=request.user,
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return Response({'message': 'All notifications marked as read'})


# Celery tasks
from celery import shared_task

@shared_task
def send_invitation_email(invitation_id):
    """Send invitation email"""
    try:
        invitation = ProjectInvitation.objects.get(id=invitation_id)
        
        # TODO: Implement email sending
        logger.info(f"Sending invitation email to {invitation.invitee_email}")
        
        # Here you would integrate with email service
        
    except ProjectInvitation.DoesNotExist:
        logger.error(f"Invitation {invitation_id} not found")


@shared_task
def create_comment_notifications(comment_id):
    """Create notifications for new comments"""
    try:
        comment = ProjectComment.objects.get(id=comment_id)
        project = comment.project
        
        # Get all collaborators except the comment author
        collaborators = project.collaborators.exclude(id=comment.user.id)
        
        # Add project owner if not the comment author
        if project.owner != comment.user:
            collaborators = collaborators.union(User.objects.filter(id=project.owner.id))
        
        # Create notifications
        for user in collaborators:
            ProjectNotification.objects.create(
                user=user,
                project=project,
                notification_type='comment_added',
                title=f'New comment on {project.name}',
                message=f'{comment.user.full_name} added a comment: {comment.content[:100]}...',
                comment_id=comment.id
            )
        
        logger.info(f"Created notifications for comment {comment_id}")
        
    except ProjectComment.DoesNotExist:
        logger.error(f"Comment {comment_id} not found")