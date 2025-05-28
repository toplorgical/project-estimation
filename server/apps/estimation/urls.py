from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.view import ProjectViewSet, ProjectResourcesViewSet, ProjectLabourViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'project-resources', ProjectResourcesViewSet, basename='project-resources')
router.register(r'project-labour', ProjectLabourViewSet, basename='project-labour')

urlpatterns = [
    path('', include(router.urls)),
]
