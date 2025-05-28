from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.view import ProjectViewSet, ProjectResourcesViewSet, ProjectLabourViewSet
from .views.view import EstimateProjectCostView, TrainModelView, UpdateMarketPricesView



router = DefaultRouter()





router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'project-resources', ProjectResourcesViewSet, basename='project-resources')
router.register(r'project-labour', ProjectLabourViewSet, basename='project-labour')





urlpatterns = [
    path('projects/<uuid:project_id>/estimate/', EstimateProjectCostView.as_view(), name='estimate-project-cost'),
    path('projects/train-model/', TrainModelView.as_view(), name='train-model'),
    path('projects/<uuid:project_id>/update-prices/', UpdateMarketPricesView.as_view(), name='update-market-prices'),
]


urlpatterns = [
    path('', include(router.urls)),
]
