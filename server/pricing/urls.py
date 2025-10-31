from django.urls import path
from . import views

urlpatterns = [
    path('suppliers/', views.SupplierListView.as_view(), name='supplier-list'),
    path('data/', views.PriceDataListView.as_view(), name='price-data-list'),
    path('alerts/', views.PriceAlertListCreateView.as_view(), name='price-alert-list-create'),
    path('alerts/<int:pk>/', views.PriceAlertDetailView.as_view(), name='price-alert-detail'),
    path('scraped-data/', views.receive_scraped_data, name='receive-scraped-data'),
    path('realtime/', views.get_realtime_pricing, name='realtime-pricing'),
    path('<str:item_type>/<int:item_id>/history/', views.get_price_history, name='price-history'),
    path('trends/', views.get_price_trends, name='price-trends'),
]