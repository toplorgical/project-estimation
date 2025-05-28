
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.estimation.urls')),  
    path('api/v1/', include('apps.user_auth.urls')),  
   
]
