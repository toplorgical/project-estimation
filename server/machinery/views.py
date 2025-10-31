from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Machinery, MachineryCategory
from .serializers import (
    MachinerySerializer,
    MachineryDetailSerializer,
    MachineryCategorySerializer,
    MachinerySearchSerializer
)


class MachineryCategoryListView(generics.ListAPIView):
    """List all machinery categories"""
    queryset = MachineryCategory.objects.filter(parent=None)
    serializer_class = MachineryCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class MachineryListView(generics.ListAPIView):
    """List all machinery with filtering and search"""
    queryset = Machinery.objects.filter(is_active=True).select_related('category')
    serializer_class = MachinerySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'brand', 'fuel_type']
    search_fields = ['name', 'description', 'model', 'brand']
    ordering_fields = ['name', 'brand', 'created_at']
    ordering = ['name']
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['location'] = self.request.query_params.get('location')
        return context


class MachineryDetailView(generics.RetrieveAPIView):
    """Retrieve machinery details with price history"""
    queryset = Machinery.objects.filter(is_active=True).select_related('category')
    serializer_class = MachineryDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['location'] = self.request.query_params.get('location')
        return context


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def machinery_search(request):
    """Advanced machinery search with complex filters"""
    serializer = MachinerySearchSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    queryset = Machinery.objects.filter(is_active=True).select_related('category')
    
    # Apply filters
    if data.get('query'):
        queryset = queryset.filter(
            Q(name__icontains=data['query']) |
            Q(description__icontains=data['query']) |
            Q(brand__icontains=data['query']) |
            Q(model__icontains=data['query']) |
            Q(sku__icontains=data['query'])
        )
    
    if data.get('category'):
        queryset = queryset.filter(category_id=data['category'])
    
    if data.get('brand'):
        queryset = queryset.filter(brand__icontains=data['brand'])
    
    if data.get('fuel_type'):
        queryset = queryset.filter(fuel_type=data['fuel_type'])
    
    # Apply ordering
    ordering = data.get('ordering', 'name')
    queryset = queryset.order_by(ordering)
    
    # Paginate results
    page = request.query_params.get('page', 1)
    page_size = min(int(request.query_params.get('page_size', 20)), 100)
    
    start = (int(page) - 1) * page_size
    end = start + page_size
    
    machinery = queryset[start:end]
    
    context = {'location': data.get('location')}
    serializer = MachinerySerializer(machinery, many=True, context=context)
    
    return Response({
        'results': serializer.data,
        'count': queryset.count(),
        'page': int(page),
        'page_size': page_size,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def machinery_suggestions(request):
    """Get machinery suggestions based on project requirements"""
    project_type = request.query_params.get('project_type')
    area = request.query_params.get('area')
    
    suggestions = []
    
    if project_type == 'residential':
        # Basic residential construction machinery
        essential_machinery = [
            'excavator', 'mixer', 'drill', 'saw', 'compactor',
            'generator', 'crane', 'loader', 'dumper', 'scaffold'
        ]
        
        for machinery_name in essential_machinery:
            machinery_items = Machinery.objects.filter(
                name__icontains=machinery_name,
                is_active=True
            ).select_related('category')[:3]
            
            if machinery_items:
                suggestions.append({
                    'category': machinery_name.title(),
                    'machinery': MachinerySerializer(machinery_items, many=True).data
                })
    
    elif project_type == 'commercial':
        # Commercial construction machinery
        commercial_machinery = [
            'tower crane', 'excavator', 'concrete pump', 'loader',
            'dumper', 'compactor', 'generator', 'hoist', 'forklift'
        ]
        
        for machinery_name in commercial_machinery:
            machinery_items = Machinery.objects.filter(
                name__icontains=machinery_name,
                is_active=True
            ).select_related('category')[:3]
            
            if machinery_items:
                suggestions.append({
                    'category': machinery_name.title(),
                    'machinery': MachinerySerializer(machinery_items, many=True).data
                })
    
    return Response({'suggestions': suggestions})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def machinery_availability(request):
    """Check machinery availability across locations"""
    machinery_ids = request.query_params.get('machinery_ids', '').split(',')
    location = request.query_params.get('location')
    
    if not machinery_ids or machinery_ids == ['']:
        return Response({'error': 'machinery_ids parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    availability_data = []
    
    for machinery_id in machinery_ids:
        try:
            machinery = Machinery.objects.get(id=int(machinery_id), is_active=True)
            
            # Get availability from price data
            from pricing.models import PriceData
            
            availability_query = PriceData.objects.filter(
                machinery=machinery,
                is_active=True,
                in_stock=True
            )
            
            if location:
                availability_query = availability_query.filter(location__icontains=location)
            
            available_locations = list(availability_query.values_list('location', flat=True).distinct())
            
            availability_data.append({
                'machinery_id': machinery.id,
                'machinery_name': machinery.name,
                'available': len(available_locations) > 0,
                'locations': available_locations,
                'suppliers': list(availability_query.values_list('supplier__name', flat=True).distinct())
            })
            
        except (Machinery.DoesNotExist, ValueError):
            availability_data.append({
                'machinery_id': machinery_id,
                'error': 'Machinery not found'
            })
    
    return Response({'availability': availability_data})