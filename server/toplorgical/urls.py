from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({"status": "healthy", "service": "toplorgical-api"})

urlpatterns = [
    path('health/', health_check, name='health'),
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/projects/', include('projects.urls')),
    path('api/v1/materials/', include('materials.urls')),
    path('api/v1/machinery/', include('machinery.urls')),
    path('api/v1/pricing/', include('pricing.urls')),
    path('api/v1/estimates/', include('estimates.urls')),
    path('api/v1/exports/', include('exports.urls')),
    path('api/v1/collaboration/', include('collaboration.urls')),
    path('api/v1/payments/', include('payments.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)