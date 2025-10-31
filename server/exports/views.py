from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.conf import settings
from django.db.models import Q
from .models import ExportJob
from .serializers import ExportJobSerializer, ExportRequestSerializer
from .tasks import generate_export
from projects.models import Project
from estimates.models import Estimate
import os


class ExportJobListView(generics.ListAPIView):
    """List user's export jobs"""
    serializer_class = ExportJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ExportJob.objects.filter(user=self.request.user)


class ExportJobDetailView(generics.RetrieveAPIView):
    """Get export job details"""
    serializer_class = ExportJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ExportJob.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_export(request):
    """Create a new export job"""
    serializer = ExportRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    user = request.user
    
    # Validate permissions
    project = None
    estimate = None
    
    if data.get('project_id'):
        project = get_object_or_404(Project, id=data['project_id'])
        if not (project.owner == user or project.collaborators.filter(id=user.id).exists()):
            return Response(
                {'error': 'You do not have permission to export this project'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    if data.get('estimate_id'):
        estimate = get_object_or_404(Estimate, id=data['estimate_id'])
        if not (estimate.project.owner == user or estimate.project.collaborators.filter(id=user.id).exists()):
            return Response(
                {'error': 'You do not have permission to export this estimate'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    # Create export job
    export_job = ExportJob.objects.create(
        user=user,
        export_type=data['export_type'],
        project=project,
        estimate=estimate,
        options=data.get('options', {})
    )
    
    # Start export task
    generate_export.delay(export_job.id)
    
    return Response(
        ExportJobSerializer(export_job).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_export(request, job_id):
    """Download completed export file"""
    export_job = get_object_or_404(ExportJob, id=job_id, user=request.user)
    
    if export_job.status != 'completed':
        return Response(
            {'error': 'Export is not completed yet'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if export_job.is_expired:
        return Response(
            {'error': 'Export file has expired'},
            status=status.HTTP_410_GONE
        )
    
    if not export_job.file_path or not os.path.exists(export_job.file_path):
        return Response(
            {'error': 'Export file not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Determine content type
    content_type = 'application/octet-stream'
    if export_job.file_name.endswith('.pdf'):
        content_type = 'application/pdf'
    elif export_job.file_name.endswith('.xlsx'):
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    # Serve file
    with open(export_job.file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{export_job.file_name}"'
        return response


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def cancel_export(request, job_id):
    """Cancel a pending export job"""
    export_job = get_object_or_404(ExportJob, id=job_id, user=request.user)
    
    if export_job.status in ['completed', 'failed']:
        return Response(
            {'error': 'Cannot cancel completed or failed export'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    export_job.status = 'failed'
    export_job.error_message = 'Cancelled by user'
    export_job.save()
    
    return Response({'message': 'Export cancelled successfully'})


# Direct export endpoints for immediate downloads
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_project_pdf(request, project_id):
    """Export project to PDF (immediate download)"""
    project = get_object_or_404(Project, id=project_id)
    user = request.user
    
    # Check permissions
    if not (project.owner == user or project.collaborators.filter(id=user.id).exists()):
        return Response(
            {'error': 'You do not have permission to export this project'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from .utils import generate_project_pdf
        pdf_content = generate_project_pdf(project, request.GET.dict())
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="project_{project.id}_{project.name}.pdf"'
        return response
    
    except Exception as e:
        return Response(
            {'error': f'Failed to generate PDF: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_estimate_pdf(request, estimate_id):
    """Export estimate to PDF (immediate download)"""
    estimate = get_object_or_404(Estimate, id=estimate_id)
    user = request.user
    
    # Check permissions
    if not (estimate.project.owner == user or estimate.project.collaborators.filter(id=user.id).exists()):
        return Response(
            {'error': 'You do not have permission to export this estimate'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from .utils import generate_estimate_pdf
        pdf_content = generate_estimate_pdf(estimate, request.GET.dict())
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="estimate_{estimate.id}_{estimate.name}.pdf"'
        return response
    
    except Exception as e:
        return Response(
            {'error': f'Failed to generate PDF: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_estimate_excel(request, estimate_id):
    """Export estimate to Excel (immediate download)"""
    estimate = get_object_or_404(Estimate, id=estimate_id)
    user = request.user
    
    # Check permissions
    if not (estimate.project.owner == user or estimate.project.collaborators.filter(id=user.id).exists()):
        return Response(
            {'error': 'You do not have permission to export this estimate'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from .utils import generate_estimate_excel
        excel_content = generate_estimate_excel(estimate, request.GET.dict())
        
        response = HttpResponse(
            excel_content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="estimate_{estimate.id}_{estimate.name}.xlsx"'
        return response
    
    except Exception as e:
        return Response(
            {'error': f'Failed to generate Excel: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )