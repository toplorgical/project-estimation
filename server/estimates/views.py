from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db import transaction
from .models import (
    Estimate, EstimateMaterialItem, EstimateMachineryItem, EstimateSubstitution
)
from .serializers import (
    EstimateSerializer,
    EstimateDetailSerializer,
    EstimateMaterialItemSerializer,
    EstimateMachineryItemSerializer,
    EstimateSubstitutionSerializer,
    GenerateEstimateSerializer,
    OptimizeEstimateSerializer
)
from projects.models import Project
from materials.models import Material
from machinery.models import Machinery
from pricing.models import PriceData
import logging

logger = logging.getLogger(__name__)


class EstimateListCreateView(generics.ListCreateAPIView):
    """List and create estimates"""
    serializer_class = EstimateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Estimate.objects.filter(
            Q(project__owner=user) | Q(project__collaborators=user)
        ).distinct().select_related('project', 'created_by')


class EstimateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an estimate"""
    serializer_class = EstimateDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Estimate.objects.filter(
            Q(project__owner=user) | Q(project__collaborators=user)
        ).select_related('project', 'created_by').prefetch_related(
            'material_items__material',
            'machinery_items__machinery',
            'substitutions'
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_estimate(request):
    """Generate a new estimate with automatic pricing"""
    serializer = GenerateEstimateSerializer(data=request.data, context={'request': request})
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        with transaction.atomic():
            # Get project
            project = Project.objects.get(id=data['project_id'])
            
            # Create estimate
            estimate = Estimate.objects.create(
                project=project,
                name=data['name'],
                description=data.get('description', ''),
                labor_cost=data.get('labor_cost', 0),
                overhead_cost=data.get('overhead_cost', 0),
                created_by=request.user
            )
            
            # Add material items
            materials_total = 0
            for material_data in data.get('materials', []):
                material = Material.objects.get(id=material_data['material_id'])
                
                # Get current price if not provided
                unit_price = material_data.get('unit_price')
                if not unit_price:
                    current_price = material.get_current_price(data.get('location'))
                    unit_price = current_price or 0
                
                material_item = EstimateMaterialItem.objects.create(
                    estimate=estimate,
                    material=material,
                    quantity=material_data['quantity'],
                    unit_price=unit_price,
                    waste_factor=material_data.get('waste_factor', 0.10),
                    supplier=material_data.get('supplier', ''),
                    supplier_location=material_data.get('supplier_location', ''),
                    notes=material_data.get('notes', '')
                )
                materials_total += material_item.total_cost
            
            # Add machinery items
            machinery_total = 0
            for machinery_data in data.get('machinery', []):
                machinery = Machinery.objects.get(id=machinery_data['machinery_id'])
                
                # Get current price if not provided
                unit_price = machinery_data.get('unit_price')
                if not unit_price:
                    rental_type = machinery_data['rental_type']
                    current_price = machinery.get_current_rental_price(
                        data.get('location'), rental_type
                    )
                    unit_price = current_price or 0
                
                machinery_item = EstimateMachineryItem.objects.create(
                    estimate=estimate,
                    machinery=machinery,
                    rental_type=machinery_data['rental_type'],
                    duration=machinery_data['duration'],
                    unit_price=unit_price,
                    transport_cost=machinery_data.get('transport_cost', 0),
                    setup_cost=machinery_data.get('setup_cost', 0),
                    supplier=machinery_data.get('supplier', ''),
                    supplier_location=machinery_data.get('supplier_location', ''),
                    notes=machinery_data.get('notes', '')
                )
                machinery_total += machinery_item.total_cost
            
            # Update estimate totals
            estimate.materials_cost = materials_total
            estimate.machinery_cost = machinery_total
            estimate.calculate_totals()
            
            # Generate substitution suggestions
            generate_substitutions.delay(estimate.id, data.get('location'))
            
            return Response(
                EstimateDetailSerializer(estimate).data,
                status=status.HTTP_201_CREATED
            )
    
    except Exception as e:
        logger.error(f"Error generating estimate: {str(e)}")
        return Response(
            {'error': f'Failed to generate estimate: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def optimize_estimate(request, estimate_id):
    """Optimize an estimate by suggesting alternatives"""
    estimate = get_object_or_404(Estimate, id=estimate_id)
    
    # Check permissions
    user = request.user
    if not (estimate.project.owner == user or estimate.project.collaborators.filter(id=user.id).exists()):
        return Response(
            {'error': 'You do not have permission to optimize this estimate'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = OptimizeEstimateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        # Generate new substitutions
        substitutions = generate_estimate_substitutions(
            estimate,
            data.get('location'),
            data['optimization_type'],
            data['max_substitutions']
        )
        
        # Calculate potential savings
        total_savings = sum(sub.cost_savings for sub in substitutions if sub.cost_savings > 0)
        
        return Response({
            'original_cost': float(estimate.total_cost),
            'potential_savings': float(total_savings),
            'optimized_cost': float(estimate.total_cost - total_savings),
            'substitutions': EstimateSubstitutionSerializer(substitutions, many=True).data
        })
    
    except Exception as e:
        logger.error(f"Error optimizing estimate {estimate_id}: {str(e)}")
        return Response(
            {'error': f'Failed to optimize estimate: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_estimate_substitutions(request, estimate_id):
    """Get substitution suggestions for an estimate"""
    estimate = get_object_or_404(Estimate, id=estimate_id)
    
    # Check permissions
    user = request.user
    if not (estimate.project.owner == user or estimate.project.collaborators.filter(id=user.id).exists()):
        return Response(
            {'error': 'You do not have permission to view this estimate'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    substitutions = estimate.substitutions.all().order_by('-cost_savings')
    serializer = EstimateSubstitutionSerializer(substitutions, many=True)
    
    return Response({'substitutions': serializer.data})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def apply_substitution(request, estimate_id, substitution_id):
    """Apply a substitution to an estimate"""
    estimate = get_object_or_404(Estimate, id=estimate_id)
    substitution = get_object_or_404(EstimateSubstitution, id=substitution_id, estimate=estimate)
    
    # Check permissions
    user = request.user
    if not (estimate.project.owner == user or estimate.project.collaborators.filter(id=user.id).exists()):
        return Response(
            {'error': 'You do not have permission to modify this estimate'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        with transaction.atomic():
            # Apply the substitution
            if substitution.original_material and substitution.alternative_material:
                # Replace material item
                material_item = EstimateMaterialItem.objects.get(
                    estimate=estimate,
                    material=substitution.original_material
                )
                material_item.material = substitution.alternative_material
                material_item.unit_price = substitution.alternative_price
                material_item.save()
            
            elif substitution.original_machinery and substitution.alternative_machinery:
                # Replace machinery item
                machinery_item = EstimateMachineryItem.objects.get(
                    estimate=estimate,
                    machinery=substitution.original_machinery
                )
                machinery_item.machinery = substitution.alternative_machinery
                machinery_item.unit_price = substitution.alternative_price
                machinery_item.save()
            
            # Mark substitution as applied
            substitution.is_applied = True
            substitution.applied_at = timezone.now()
            substitution.save()
            
            # Recalculate estimate totals
            estimate.update_material_costs()
            estimate.update_machinery_costs()
            
            return Response({
                'message': 'Substitution applied successfully',
                'new_total_cost': float(estimate.total_cost)
            })
    
    except Exception as e:
        logger.error(f"Error applying substitution {substitution_id}: {str(e)}")
        return Response(
            {'error': f'Failed to apply substitution: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def generate_estimate_substitutions(estimate, location, optimization_type='cost', max_substitutions=5):
    """Generate substitution suggestions for an estimate"""
    substitutions = []
    
    # Generate material substitutions
    for material_item in estimate.material_items.all():
        alternatives = find_material_alternatives(
            material_item.material,
            location,
            optimization_type
        )
        
        for alternative in alternatives[:2]:  # Top 2 alternatives per item
            if len(substitutions) >= max_substitutions:
                break
            
            substitution = EstimateSubstitution(
                estimate=estimate,
                original_material=material_item.material,
                alternative_material=alternative['material'],
                original_price=material_item.unit_price,
                alternative_price=alternative['price'],
                reason=alternative['reason'],
                confidence_score=alternative['confidence']
            )
            substitution.save()
            substitutions.append(substitution)
    
    # Generate machinery substitutions
    for machinery_item in estimate.machinery_items.all():
        if len(substitutions) >= max_substitutions:
            break
        
        alternatives = find_machinery_alternatives(
            machinery_item.machinery,
            location,
            optimization_type
        )
        
        for alternative in alternatives[:2]:  # Top 2 alternatives per item
            if len(substitutions) >= max_substitutions:
                break
            
            substitution = EstimateSubstitution(
                estimate=estimate,
                original_machinery=machinery_item.machinery,
                alternative_machinery=alternative['machinery'],
                original_price=machinery_item.unit_price,
                alternative_price=alternative['price'],
                reason=alternative['reason'],
                confidence_score=alternative['confidence']
            )
            substitution.save()
            substitutions.append(substitution)
    
    return substitutions


def find_material_alternatives(material, location, optimization_type):
    """Find alternative materials"""
    alternatives = []
    
    # Find materials in the same category
    similar_materials = Material.objects.filter(
        category=material.category,
        is_active=True
    ).exclude(id=material.id)
    
    for alt_material in similar_materials:
        current_price = alt_material.get_current_price(location)
        if current_price:
            alternatives.append({
                'material': alt_material,
                'price': current_price,
                'reason': f'Alternative {alt_material.category.name} with similar specifications',
                'confidence': 0.8
            })
    
    # Sort by optimization type
    if optimization_type == 'cost':
        alternatives.sort(key=lambda x: x['price'])
    
    return alternatives


def find_machinery_alternatives(machinery, location, optimization_type):
    """Find alternative machinery"""
    alternatives = []
    
    # Find machinery in the same category
    similar_machinery = Machinery.objects.filter(
        category=machinery.category,
        is_active=True
    ).exclude(id=machinery.id)
    
    for alt_machinery in similar_machinery:
        current_price = alt_machinery.get_current_rental_price(location, 'daily')
        if current_price:
            alternatives.append({
                'machinery': alt_machinery,
                'price': current_price,
                'reason': f'Alternative {alt_machinery.category.name} with similar capacity',
                'confidence': 0.7
            })
    
    # Sort by optimization type
    if optimization_type == 'cost':
        alternatives.sort(key=lambda x: x['price'])
    
    return alternatives


# Celery task for async substitution generation
from celery import shared_task

@shared_task
def generate_substitutions(estimate_id, location=None):
    """Generate substitutions asynchronously"""
    try:
        estimate = Estimate.objects.get(id=estimate_id)
        generate_estimate_substitutions(estimate, location)
        logger.info(f"Generated substitutions for estimate {estimate_id}")
    except Estimate.DoesNotExist:
        logger.error(f"Estimate {estimate_id} not found")
    except Exception as e:
        logger.error(f"Error generating substitutions for estimate {estimate_id}: {str(e)}")