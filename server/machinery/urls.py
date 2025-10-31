from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.MachineryCategoryListView.as_view(), name='machinery-categories'),
    path('', views.MachineryListView.as_view(), name='machinery-list'),
    path('<int:pk>/', views.MachineryDetailView.as_view(), name='machinery-detail'),
    path('search/', views.machinery_search, name='machinery-search'),
    path('suggestions/', views.machinery_suggestions, name='machinery-suggestions'),
    path('availability/', views.machinery_availability, name='machinery-availability'),
]