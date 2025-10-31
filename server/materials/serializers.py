from rest_framework import serializers
from .models import Material, MaterialCategory


class MaterialCategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    materials_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MaterialCategory
        fields = [
            'id', 'name', 'description', 'parent',
            'subcategories', 'materials_count', 'created_at'
        ]
    
    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return MaterialCategorySerializer(obj.subcategories.all(), many=True).data
        return []
    
    def get_materials_count(self, obj):
        return obj.materials.filter(is_active=True).count()


class MaterialSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    current_price = serializers.SerializerMethodField()
    volume = serializers.ReadOnlyField()
    
    class Meta:
        model = Material
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'sku', 'unit', 'brand', 'specifications',
            'length', 'width', 'height', 'weight', 'volume',
            'current_price', 'is_active', 'created_at', 'updated_at'
        ]
    
    def get_current_price(self, obj):
        location = self.context.get('location')
        price = obj.get_current_price(location)
        return float(price) if price else None


class MaterialDetailSerializer(MaterialSerializer):
    price_history = serializers.SerializerMethodField()
    
    class Meta(MaterialSerializer.Meta):
        fields = MaterialSerializer.Meta.fields + ['price_history']
    
    def get_price_history(self, obj):
        history = obj.get_price_history(days=30)
        return [{
            'date': item.created_at.date(),
            'price': float(item.price),
            'supplier': item.supplier.name if item.supplier else None
        } for item in history[:10]]  # Last 10 price points


class MaterialSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=False, allow_blank=True)
    category = serializers.IntegerField(required=False)
    brand = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    unit = serializers.ChoiceField(choices=Material.UNIT_CHOICES, required=False)
    ordering = serializers.ChoiceField(
        choices=[
            'name', '-name', 'price', '-price',
            'brand', '-brand', 'created_at', '-created_at'
        ],
        required=False,
        default='name'
    )