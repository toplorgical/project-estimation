from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from ..models import Project, ProjectResources, ProjectLabour
from ..serializers.serializer import ProjectSerializer, ProjectResourcesSerializer, ProjectLabourSerializer
from ..repositories.repository import ProjectRepository, ProjectResourcesRepository, ProjectLabourRepository







from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Project
from estimation.services import ProjectEstimationService
import logging

logger = logging.getLogger(__name__)

class EstimateProjectCostView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, project_id):
        """
        Estimate the cost of a project
        Parameters:
        - method: (optional) 'ml', 'scraping', or 'auto'
        """
        method = request.data.get('method', 'auto')
        
        estimation_service = ProjectEstimationService()
        success, estimated_cost, method_used = estimation_service.estimate_project_cost(project_id, method)
        
        if success:
            return Response({
                'status': 'success',
                'estimated_cost': estimated_cost,
                'method_used': method_used,
                'project_id': project_id
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': 'Could not estimate project cost',
                'project_id': project_id
            }, status=status.HTTP_400_BAD_REQUEST)

class TrainModelView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Trigger model training with current data"""
        estimation_service = ProjectEstimationService()
        success = estimation_service.train_ml_model()
        
        if success:
            return Response({
                'status': 'success',
                'message': 'Model training completed'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': 'Model training failed'
            }, status=status.HTTP_400_BAD_REQUEST)

class UpdateMarketPricesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, project_id):
        """Update market prices for a project's resources and labour"""
        try:
            project = Project.objects.get(pk=project_id, user_model=request.user)
            estimation_service = ProjectEstimationService()
            estimated_cost = estimation_service._estimate_with_scraping(project)
            
            if estimated_cost:
                return Response({
                    'status': 'success',
                    'message': 'Market prices updated',
                    'estimated_cost': estimated_cost,
                    'project_id': project_id
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Failed to update market prices',
                    'project_id': project_id
                }, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Project not found'
            }, status=status.HTTP_404_NOT_FOUND)






#crud
class ProjectViewSet(viewsets.ViewSet):
    def list(self, request):
        projects = ProjectRepository.get_all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = ProjectRepository.create(serializer.validated_data)
        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        project = ProjectRepository.get_by_id(pk)
        if not project:
            raise NotFound("Project not found")
        return Response(ProjectSerializer(project).data)

    def update(self, request, pk=None):
        project = ProjectRepository.get_by_id(pk)
        if not project:
            raise NotFound("Project not found")
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_project = ProjectRepository.update(pk, serializer.validated_data)
        return Response(ProjectSerializer(updated_project).data)

    def destroy(self, request, pk=None):
        if not ProjectRepository.delete(pk):
            raise NotFound("Project not found")
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectResourcesViewSet(viewsets.ViewSet):
    def list(self, request, project_pk=None):
        resources = ProjectResourcesRepository.get_all_by_project(project_pk)
        serializer = ProjectResourcesSerializer(resources, many=True)
        return Response(serializer.data)

    def create(self, request, project_pk=None):
        serializer = ProjectResourcesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resource = ProjectResourcesRepository.create(project_pk, serializer.validated_data)
        return Response(ProjectResourcesSerializer(resource).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None, project_pk=None):
        resource = ProjectResourcesRepository.get_by_id(project_pk, pk)
        if not resource:
            raise NotFound("Project resource not found")
        return Response(ProjectResourcesSerializer(resource).data)

    def update(self, request, pk=None, project_pk=None):
        resource = ProjectResourcesRepository.get_by_id(project_pk, pk)
        if not resource:
            raise NotFound("Project resource not found")
        serializer = ProjectResourcesSerializer(resource, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_resource = ProjectResourcesRepository.update(project_pk, pk, serializer.validated_data)
        return Response(ProjectResourcesSerializer(updated_resource).data)

    def destroy(self, request, pk=None, project_pk=None):
        if not ProjectResourcesRepository.delete(project_pk, pk):
            raise NotFound("Project resource not found")
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectLabourViewSet(viewsets.ViewSet):
    def list(self, request, project_pk=None):
        labour = ProjectLabourRepository.get_all_by_project(project_pk)
        serializer = ProjectLabourSerializer(labour, many=True)
        return Response(serializer.data)

    def create(self, request, project_pk=None):
        serializer = ProjectLabourSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        labour = ProjectLabourRepository.create(project_pk, serializer.validated_data)
        return Response(ProjectLabourSerializer(labour).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None, project_pk=None):
        labour = ProjectLabourRepository.get_by_id(project_pk, pk)
        if not labour:
            raise NotFound("Project labour not found")
        return Response(ProjectLabourSerializer(labour).data)

    def update(self, request, pk=None, project_pk=None):
        labour = ProjectLabourRepository.get_by_id(project_pk, pk)
        if not labour:
            raise NotFound("Project labour not found")
        serializer = ProjectLabourSerializer(labour, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_labour = ProjectLabourRepository.update(project_pk, pk, serializer.validated_data)
        return Response(ProjectLabourSerializer(updated_labour).data)

    def destroy(self, request, pk=None, project_pk=None):
        if not ProjectLabourRepository.delete(project_pk, pk):
            raise NotFound("Project labour not found")
        return Response(status=status.HTTP_204_NO_CONTENT)
