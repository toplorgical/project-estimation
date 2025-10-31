from django.urls import path
from . import views

urlpatterns = [
    # Invitations
    path('invitations/', views.ProjectInvitationListView.as_view(), name='invitation-list'),
    path('invitations/send/', views.send_invitation, name='send-invitation'),
    path('invitations/respond/', views.respond_to_invitation, name='respond-invitation'),
    
    # Activity logs
    path('projects/<int:project_id>/activity/', views.ActivityLogListView.as_view(), name='activity-log-list'),
    
    # Comments
    path('projects/<int:project_id>/comments/', views.ProjectCommentListCreateView.as_view(), name='project-comment-list-create'),
    path('projects/<int:project_id>/comments/<int:pk>/', views.ProjectCommentDetailView.as_view(), name='project-comment-detail'),
    path('projects/<int:project_id>/comments/<int:comment_id>/reply/', views.add_comment_reply, name='add-comment-reply'),
    path('projects/<int:project_id>/comments/<int:comment_id>/resolve/', views.resolve_comment, name='resolve-comment'),
    
    # Notifications
    path('notifications/', views.ProjectNotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark-notification-read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
]