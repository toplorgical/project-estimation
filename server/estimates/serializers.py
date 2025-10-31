from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Estimate, EstimateMaterialItem, EstimateMachineryItem, EstimateSubstitution
)
from projects.models import Project
from materials.models import Material
from machinery.models import Machinery

User = get_user_model()


class EstimateMaterialItemSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    material_unit = serializers.CharField(source='material.unit', read_only=True)
    
    class Meta:
        model = EstimateMaterialItem
        fields = [
            'id', 'material', 'material_name', 'material_unit',
            'quantity', 'unit_price', 'total_cost', 'waste_factor',
            'supplier', 'supplier_location', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'total_cost', 'created_at', 'updated_at')


class EstimateMachineryItemSerializer(serializers.ModelSerializer):
    machinery_name = serializers.CharField(source='machinery.name', read_only=True)
    
    class Meta:
        model = EstimateMachineryItem
        fields = [
            'id', 'machinery', 'machinery_name', 'rental_type',
            'duration', 'unit_price', 'transport_cost', 'setup_cost',
            'total_cost', 'supplier', 'supplier_location', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'total_cost', 'created_at', 'updated_at')


class EstimateSubstitutionSerializer(serializers.ModelSerializer):
    original_item_name = serializers.SerializerMethodField()
    alternative_item_name = serializers.SerializerMethodField()
    
    class Meta:
        model = EstimateSubstitution
        fields = [
            'id', 'original_material', 'original_machinery',
            'alternative_material', 'alternative_machinery',
            'original_price', 'alternative_price', 'cost_savings',
            'reason', 'confidence_score', 'is_applied', 'applied_at',
            'original_item_name', 'alternative_item_name', 'created_at'
        ]
        read_only_fields = ('id', 'cost_savings', 'created_at')
    
    def get_original_item_name(self, obj):
        original = obj.original_material or obj.original_machinery
        return original.name if original else None
    
    def get_alternative_item_name(self, obj):
        alternative = obj.alternative_material or obj.alternative_machinery
        return alternative.name if alternative else None


class EstimateSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    material_items_count = serializers.SerializerMethodField()
    machinery_items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Estimate
        fields = [
            'id', 'project', 'project_name', 'name', 'description', 'status',
            'materials_cost', 'labor_cost', 'machinery_cost', 'overhead_cost',
            'subtotal', 'vat_rate', 'vat_amount', 'total_cost',
            'created_by', 'created_by_name', 'material_items_count',
            'machinery_items_count', 'created_at', 'updated_at'
        ]
        read_only_fields = (
            'id', 'subtotal', 'vat_amount', 'total_cost',
            'created_by', 'created_at', 'updated_at'
        )
    
    def get_material_items_count(self, obj):
        return obj.material_items.count()
    
    def get_machinery_items_count(self, obj):
        return obj.machinery_items.count()
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class EstimateDetailSerializer(EstimateSerializer):
    material_items = EstimateMaterialItemSerializer(many=True, read_only=True)
    machinery_items = EstimateMachineryItemSerializer(many=True, read_only=True)
    substitutions = EstimateSubstitutionSerializer(many=True, read_only=True)
    
    class Meta(EstimateSerializer.Meta):
        fields = EstimateSerializer.Meta.fields + [
            'material_items', 'machinery_items', 'substitutions'
        ]


class GenerateEstimateSerializer(serializers.Serializer):
    """Serializer for generating estimates"""
    project_id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    
    # Material items
    materials = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    
    # Machinery items
    machinery = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    
    # Cost overrides
    labor_cost = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        default=0
    )
    overhead_cost = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        default=0
    )
    
    # Location for pricing
    location = serializers.CharField(required=False, allow_blank=True)
    
    def validate_project_id(self, value):
        user = self.context['request'].user
        try:
            project = Project.objects.get(id=value)
            # Check if user has access to the project
            if not (project.owner == user or project.collaborators.filter(id=user.id).exists()):
                raise serializers.ValidationError("You don't have access to this project")
            return value
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found")
    
    def validate_materials(self, value):
        for item in value:
            required_fields = ['material_id', 'quantity', 'unit_price']
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(f"Material item missing required field: {field}")
            
            # Validate material exists
            try:
                Material.objects.get(id=item['material_id'], is_active=True)
            except Material.DoesNotExist:
                raise serializers.ValidationError(f"Material {item['material_id']} not found")
        
        return value
    
    def validate_machinery(self, value):
        for item in value:
            required_fields = ['machinery_id', 'rental_type', 'duration', 'unit_price']
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(f"Machinery item missing required field: {field}")
            
            # Validate machinery exists
            try:
                Machinery.objects.get(id=item['machinery_id'], is_active=True)
            except Machinery.DoesNotExist:
                raise serializers.ValidationError(f"Machinery {item['machinery_id']} not found")
        
        return value


class OptimizeEstimateSerializer(serializers.Serializer):
    """Serializer for estimate optimization"""
    optimization_type = serializers.ChoiceField(
        choices=['cost', 'time', 'quality'],
        default='cost'
    )
    max_substitutions = serializers.IntegerField(default=5, min_value=1, max_value=20)
    location = serializers.CharField(required=False, allow_blank=True)
    budget_limit = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False
    )