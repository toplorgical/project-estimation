from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Min, Max
from django.utils import timezone
from datetime import timedelta
from .models import Supplier, PriceData, PriceAlert, PriceHistory
from .serializers import (
    SupplierSerializer,
    PriceDataSerializer,
    PriceAlertSerializer,
    PriceHistorySerializer,
    ScrapedDataSerializer,
    RealtimePricingSerializer
)
from materials.models import Material
from machinery.models import Machinery


class SupplierListView(generics.ListAPIView):
    """List all suppliers"""
    queryset = Supplier.objects.filter(is_active=True)
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]


class PriceDataListView(generics.ListAPIView):
    """List price data with filtering"""
    serializer_class = PriceDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = PriceData.objects.filter(is_active=True).select_related(
            'supplier', 'material', 'machinery'
        )
        
        # Filter by item type
        item_type = self.request.query_params.get('item_type')
        if item_type == 'material':
            queryset = queryset.filter(material__isnull=False)
        elif item_type == 'machinery':
            queryset = queryset.filter(machinery__isnull=False)
        
        # Filter by location
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Filter by supplier
        supplier_id = self.request.query_params.get('supplier')
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        
        return queryset.order_by('-created_at')


class PriceAlertListCreateView(generics.ListCreateAPIView):
    """List and create price alerts"""
    serializer_class = PriceAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PriceAlert.objects.filter(
            user=self.request.user,
            is_active=True
        ).select_related('material', 'machinery')


class PriceAlertDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a price alert"""
    serializer_class = PriceAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PriceAlert.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # For Scrapy service
def receive_scraped_data(request):
    """Receive scraped data from Scrapy service"""
    serializer = ScrapedDataSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        # Get or create supplier
        supplier, created = Supplier.objects.get_or_create(
            name=data['supplier'],
            defaults={
                'website': data.get('supplier_url', ''),
                'is_active': True
            }
        )
        
        # Update last scraped time
        supplier.last_scraped = timezone.now()
        supplier.save()
        
        # Try to match with existing material or machinery
        material = None
        machinery = None
        
        # Simple matching logic - can be enhanced
        if data.get('category'):
            # Try to find material first
            material = Material.objects.filter(
                name__icontains=data['name'],
                category__name__icontains=data['category']
            ).first()
            
            # If not found, try machinery
            if not material:
                machinery = Machinery.objects.filter(
                    name__icontains=data['name'],
                    category__name__icontains=data['category']
                ).first()
        
        # Create or update price data
        price_data, created = PriceData.objects.update_or_create(
            supplier=supplier,
            material=material,
            machinery=machinery,
            sku=data.get('sku', ''),
            defaults={
                'price': data.get('price', 0),
                'unit': data.get('unit', ''),
                'rental_price_daily': data.get('rental_price_daily'),
                'rental_price_weekly': data.get('rental_price_weekly'),
                'in_stock': data.get('in_stock', True),
                'stock_quantity': data.get('stock_quantity'),
                'location': data.get('location', ''),
                'source_url': data.get('product_url', ''),
                'scraped_at': timezone.now(),
                'is_active': True
            }
        )
        
        return Response({
            'message': 'Data processed successfully',
            'created': created,
            'price_data_id': price_data.id
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to process data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def get_realtime_pricing(request):
    """Get real-time pricing for specified items"""
    serializer = RealtimePricingSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    items = data['items']
    location = data.get('location')
    item_type = data.get('item_type', 'both')
    
    pricing_data = []
    
    for item_id in items:
        item_pricing = {'item_id': item_id, 'prices': []}
        
        # Get material pricing
        if item_type in ['material', 'both']:
            try:
                material = Material.objects.get(id=item_id)
                price_query = PriceData.objects.filter(
                    material=material,
                    is_active=True
                )
                
                if location:
                    price_query = price_query.filter(location__icontains=location)
                
                prices = price_query.select_related('supplier').order_by('price')[:5]
                
                for price in prices:
                    item_pricing['prices'].append({
                        'supplier': price.supplier.name,
                        'price': float(price.price),
                        'unit': price.unit,
                        'in_stock': price.in_stock,
                        'location': price.location,
                        'updated_at': price.updated_at
                    })
                
                item_pricing['item_name'] = material.name
                item_pricing['item_type'] = 'material'
                
            except Material.DoesNotExist:
                pass
        
        # Get machinery pricing
        if item_type in ['machinery', 'both'] and not item_pricing['prices']:
            try:
                machinery = Machinery.objects.get(id=item_id)
                price_query = PriceData.objects.filter(
                    machinery=machinery,
                    is_active=True
                )
                
                if location:
                    price_query = price_query.filter(location__icontains=location)
                
                prices = price_query.select_related('supplier').order_by('price')[:5]
                
                for price in prices:
                    item_pricing['prices'].append({
                        'supplier': price.supplier.name,
                        'price': float(price.price) if price.price else None,
                        'rental_price_daily': float(price.rental_price_daily) if price.rental_price_daily else None,
                        'rental_price_weekly': float(price.rental_price_weekly) if price.rental_price_weekly else None,
                        'in_stock': price.in_stock,
                        'location': price.location,
                        'updated_at': price.updated_at
                    })
                
                item_pricing['item_name'] = machinery.name
                item_pricing['item_type'] = 'machinery'
                
            except Machinery.DoesNotExist:
                pass
        
        pricing_data.append(item_pricing)
    
    return Response({'pricing': pricing_data})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_price_history(request, item_type, item_id):
    """Get price history for a specific item"""
    days = int(request.query_params.get('days', 30))
    location = request.query_params.get('location')
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    if item_type == 'material':
        try:
            material = Material.objects.get(id=item_id)
            history_query = PriceHistory.objects.filter(
                material=material,
                date__range=[start_date, end_date]
            )
        except Material.DoesNotExist:
            return Response({'error': 'Material not found'}, status=status.HTTP_404_NOT_FOUND)
    
    elif item_type == 'machinery':
        try:
            machinery = Machinery.objects.get(id=item_id)
            history_query = PriceHistory.objects.filter(
                machinery=machinery,
                date__range=[start_date, end_date]
            )
        except Machinery.DoesNotExist:
            return Response({'error': 'Machinery not found'}, status=status.HTTP_404_NOT_FOUND)
    
    else:
        return Response({'error': 'Invalid item type'}, status=status.HTTP_400_BAD_REQUEST)
    
    if location:
        history_query = history_query.filter(location__icontains=location)
    
    history = history_query.order_by('date')
    serializer = PriceHistorySerializer(history, many=True)
    
    return Response({
        'item_type': item_type,
        'item_id': item_id,
        'location': location,
        'days': days,
        'price_history': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_price_trends(request):
    """Get price trends and analytics"""
    item_type = request.query_params.get('item_type', 'material')
    location = request.query_params.get('location')
    days = int(request.query_params.get('days', 30))
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get trending items (items with significant price changes)
    if item_type == 'material':
        trending_query = PriceHistory.objects.filter(
            material__isnull=False,
            date__range=[start_date, end_date]
        )
    else:
        trending_query = PriceHistory.objects.filter(
            machinery__isnull=False,
            date__range=[start_date, end_date]
        )
    
    if location:
        trending_query = trending_query.filter(location__icontains=location)
    
    # Calculate price changes
    trending_items = []
    for item in trending_query.values('material', 'machinery').distinct():
        if item_type == 'material' and item['material']:
            item_history = trending_query.filter(material=item['material']).order_by('date')
        elif item_type == 'machinery' and item['machinery']:
            item_history = trending_query.filter(machinery=item['machinery']).order_by('date')
        else:
            continue
        
        if item_history.count() >= 2:
            first_price = item_history.first().avg_price
            last_price = item_history.last().avg_price
            
            if first_price and last_price and first_price > 0:
                change_percent = ((last_price - first_price) / first_price) * 100
                
                if abs(change_percent) > 5:  # Only include significant changes
                    trending_items.append({
                        'item_id': item['material'] or item['machinery'],
                        'item_type': item_type,
                        'price_change_percent': round(change_percent, 2),
                        'first_price': float(first_price),
                        'last_price': float(last_price)
                    })
    
    # Sort by absolute change percentage
    trending_items.sort(key=lambda x: abs(x['price_change_percent']), reverse=True)
    
    return Response({
        'trending_items': trending_items[:10],  # Top 10 trending items
        'period_days': days,
        'location': location
    })