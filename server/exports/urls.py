from django.urls import path
from . import views

urlpatterns = [
    # Export job management
    path('jobs/', views.ExportJobListView.as_view(), name='export-job-list'),
    path('jobs/<int:pk>/', views.ExportJobDetailView.as_view(), name='export-job-detail'),
    path('create/', views.create_export, name='create-export'),
    path('jobs/<int:job_id>/download/', views.download_export, name='download-export'),
    path('jobs/<int:job_id>/cancel/', views.cancel_export, name='cancel-export'),
    
    # Direct export endpoints
    path('projects/<int:project_id>/pdf/', views.export_project_pdf, name='export-project-pdf'),
    path('estimates/<int:estimate_id>/pdf/', views.export_estimate_pdf, name='export-estimate-pdf'),
    path('estimates/<int:estimate_id>/excel/', views.export_estimate_excel, name='export-estimate-excel'),
]