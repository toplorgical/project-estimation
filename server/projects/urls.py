from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('<int:project_id>/collaborators/', views.ProjectCollaboratorListView.as_view(), name='project-collaborators'),
    path('<int:project_id>/invite/', views.invite_collaborator, name='invite-collaborator'),
    path('<int:project_id>/collaborators/<int:user_id>/', views.remove_collaborator, name='remove-collaborator'),
]