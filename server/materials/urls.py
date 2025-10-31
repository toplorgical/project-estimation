from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.MaterialCategoryListView.as_view(), name='material-categories'),
    path('', views.MaterialListView.as_view(), name='material-list'),
    path('<int:pk>/', views.MaterialDetailView.as_view(), name='material-detail'),
    path('search/', views.material_search, name='material-search'),
    path('suggestions/', views.material_suggestions, name='material-suggestions'),
]