from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Material, MaterialCategory
from .serializers import (
    MaterialSerializer,
    MaterialDetailSerializer,
    MaterialCategorySerializer,
    MaterialSearchSerializer
)


class MaterialCategoryListView(generics.ListAPIView):
    """List all material categories"""
    queryset = MaterialCategory.objects.filter(parent=None)
    serializer_class = MaterialCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class MaterialListView(generics.ListAPIView):
    """List all materials with filtering and search"""
    queryset = Material.objects.filter(is_active=True).select_related('category')
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'brand', 'unit']
    search_fields = ['name', 'description', 'sku', 'brand']
    ordering_fields = ['name', 'brand', 'created_at']
    ordering = ['name']
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['location'] = self.request.query_params.get('location')
        return context


class MaterialDetailView(generics.RetrieveAPIView):
    """Retrieve material details with price history"""
    queryset = Material.objects.filter(is_active=True).select_related('category')
    serializer_class = MaterialDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['location'] = self.request.query_params.get('location')
        return context


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def material_search(request):
    """Advanced material search with complex filters"""
    serializer = MaterialSearchSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    queryset = Material.objects.filter(is_active=True).select_related('category')
    
    # Apply filters
    if data.get('query'):
        queryset = queryset.filter(
            Q(name__icontains=data['query']) |
            Q(description__icontains=data['query']) |
            Q(brand__icontains=data['query']) |
            Q(sku__icontains=data['query'])
        )
    
    if data.get('category'):
        queryset = queryset.filter(category_id=data['category'])
    
    if data.get('brand'):
        queryset = queryset.filter(brand__icontains=data['brand'])
    
    if data.get('unit'):
        queryset = queryset.filter(unit=data['unit'])
    
    # Price filtering would require joining with pricing data
    # This is a simplified version
    
    # Apply ordering
    ordering = data.get('ordering', 'name')
    if ordering == 'price':
        # Would need to order by current price from pricing table
        pass
    else:
        queryset = queryset.order_by(ordering)
    
    # Paginate results
    page = request.query_params.get('page', 1)
    page_size = min(int(request.query_params.get('page_size', 20)), 100)
    
    start = (int(page) - 1) * page_size
    end = start + page_size
    
    materials = queryset[start:end]
    
    context = {'location': data.get('location')}
    serializer = MaterialSerializer(materials, many=True, context=context)
    
    return Response({
        'results': serializer.data,
        'count': queryset.count(),
        'page': int(page),
        'page_size': page_size,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def material_suggestions(request):
    """Get material suggestions based on project requirements"""
    project_type = request.query_params.get('project_type')
    area = request.query_params.get('area')
    
    suggestions = []
    
    if project_type == 'residential':
        # Basic residential construction materials
        essential_materials = [
            'concrete', 'steel', 'brick', 'timber', 'insulation',
            'roofing', 'flooring', 'paint', 'electrical', 'plumbing'
        ]
        
        for material_name in essential_materials:
            materials = Material.objects.filter(
                name__icontains=material_name,
                is_active=True
            ).select_related('category')[:3]
            
            if materials:
                suggestions.append({
                    'category': material_name.title(),
                    'materials': MaterialSerializer(materials, many=True).data
                })
    
    return Response({'suggestions': suggestions})