from rest_framework import serializers
from .models import Machinery, MachineryCategory


class MachineryCategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    machinery_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MachineryCategory
        fields = [
            'id', 'name', 'description', 'parent',
            'subcategories', 'machinery_count', 'created_at'
        ]
    
    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return MachineryCategorySerializer(obj.subcategories.all(), many=True).data
        return []
    
    def get_machinery_count(self, obj):
        return obj.machinery.filter(is_active=True).count()


class MachinerySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    current_rental_price_daily = serializers.SerializerMethodField()
    current_rental_price_weekly = serializers.SerializerMethodField()
    current_purchase_price = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()
    
    class Meta:
        model = Machinery
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'brand', 'model', 'sku', 'specifications', 'power', 'fuel_type',
            'length', 'width', 'height', 'weight', 'capacity', 'max_load',
            'current_rental_price_daily', 'current_rental_price_weekly',
            'current_purchase_price', 'availability',
            'is_active', 'created_at', 'updated_at'
        ]
    
    def get_current_rental_price_daily(self, obj):
        location = self.context.get('location')
        price = obj.get_current_rental_price(location, 'daily')
        return float(price) if price else None
    
    def get_current_rental_price_weekly(self, obj):
        location = self.context.get('location')
        price = obj.get_current_rental_price(location, 'weekly')
        return float(price) if price else None
    
    def get_current_purchase_price(self, obj):
        location = self.context.get('location')
        price = obj.get_purchase_price(location)
        return float(price) if price else None
    
    def get_availability(self, obj):
        location = self.context.get('location')
        return obj.get_availability(location)


class MachineryDetailSerializer(MachinerySerializer):
    price_history = serializers.SerializerMethodField()
    
    class Meta(MachinerySerializer.Meta):
        fields = MachinerySerializer.Meta.fields + ['price_history']
    
    def get_price_history(self, obj):
        history = obj.get_price_history(days=30)
        return [{
            'date': item.created_at.date(),
            'rental_price_daily': float(item.rental_price_daily) if item.rental_price_daily else None,
            'rental_price_weekly': float(item.rental_price_weekly) if item.rental_price_weekly else None,
            'purchase_price': float(item.price) if item.price else None,
            'supplier': item.supplier.name if item.supplier else None
        } for item in history[:10]]


class MachinerySearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=False, allow_blank=True)
    category = serializers.IntegerField(required=False)
    brand = serializers.CharField(required=False, allow_blank=True)
    fuel_type = serializers.ChoiceField(choices=Machinery.FUEL_TYPES, required=False)
    location = serializers.CharField(required=False, allow_blank=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    rental_type = serializers.ChoiceField(
        choices=['daily', 'weekly', 'purchase'],
        required=False,
        default='daily'
    )
    ordering = serializers.ChoiceField(
        choices=[
            'name', '-name', 'brand', '-brand',
            'created_at', '-created_at'
        ],
        required=False,
        default='name'
    )