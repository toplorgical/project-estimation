from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Project, ProjectCollaborator
from .serializers import (
    ProjectSerializer,
    ProjectDetailSerializer,
    ProjectCollaboratorSerializer,
    InviteCollaboratorSerializer
)

User = get_user_model()


class ProjectListCreateView(generics.ListCreateAPIView):
    """List user projects and create new projects"""
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(
            Q(owner=user) | Q(collaborators=user)
        ).distinct().select_related('owner').prefetch_related('collaborators')


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a project"""
    serializer_class = ProjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(
            Q(owner=user) | Q(collaborators=user)
        ).select_related('owner').prefetch_related('collaborators')


class ProjectCollaboratorListView(generics.ListAPIView):
    """List project collaborators"""
    serializer_class = ProjectCollaboratorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id)
        
        # Check if user has access to the project
        user = self.request.user
        if not (project.owner == user or project.collaborators.filter(id=user.id).exists()):
            return ProjectCollaborator.objects.none()
        
        return ProjectCollaborator.objects.filter(project=project).select_related('user')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def invite_collaborator(request, project_id):
    """Invite a user to collaborate on a project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user is project owner or admin
    user = request.user
    if project.owner != user:
        collaborator = ProjectCollaborator.objects.filter(
            project=project, user=user, role='admin'
        ).first()
        if not collaborator:
            return Response(
                {'error': 'You do not have permission to invite collaborators'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    serializer = InviteCollaboratorSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        role = serializer.validated_data['role']
        
        try:
            invited_user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'User with this email does not exist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is already a collaborator
        if ProjectCollaborator.objects.filter(project=project, user=invited_user).exists():
            return Response(
                {'error': 'User is already a collaborator on this project'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create collaboration
        collaboration = ProjectCollaborator.objects.create(
            project=project,
            user=invited_user,
            role=role
        )
        
        # TODO: Send invitation email
        
        return Response(
            ProjectCollaboratorSerializer(collaboration).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_collaborator(request, project_id, user_id):
    """Remove a collaborator from a project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user is project owner or admin
    user = request.user
    if project.owner != user:
        collaborator = ProjectCollaborator.objects.filter(
            project=project, user=user, role='admin'
        ).first()
        if not collaborator:
            return Response(
                {'error': 'You do not have permission to remove collaborators'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    try:
        collaboration = ProjectCollaborator.objects.get(
            project=project, user_id=user_id
        )
        collaboration.delete()
        return Response({'message': 'Collaborator removed successfully'})
    except ProjectCollaborator.DoesNotExist:
        return Response(
            {'error': 'Collaboration not found'},
            status=status.HTTP_404_NOT_FOUND
        )