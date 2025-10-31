from django.urls import path
from . import views

urlpatterns = [
    path('', views.EstimateListCreateView.as_view(), name='estimate-list-create'),
    path('<int:pk>/', views.EstimateDetailView.as_view(), name='estimate-detail'),
    path('generate/', views.generate_estimate, name='generate-estimate'),
    path('<int:estimate_id>/optimize/', views.optimize_estimate, name='optimize-estimate'),
    path('<int:estimate_id>/substitutions/', views.get_estimate_substitutions, name='estimate-substitutions'),
    path('<int:estimate_id>/substitutions/<int:substitution_id>/apply/', views.apply_substitution, name='apply-substitution'),
]