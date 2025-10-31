from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Supplier, PriceData, PriceAlert, PriceHistory
from materials.models import Material
from machinery.models import Machinery

User = get_user_model()


class SupplierSerializer(serializers.ModelSerializer):
    materials_count = serializers.SerializerMethodField()
    machinery_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'website', 'contact_email', 'phone',
            'address', 'locations', 'is_active', 'last_scraped',
            'materials_count', 'machinery_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'last_scraped', 'created_at', 'updated_at')
    
    def get_materials_count(self, obj):
        return obj.price_data.filter(material__isnull=False).count()
    
    def get_machinery_count(self, obj):
        return obj.price_data.filter(machinery__isnull=False).count()


class PriceDataSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    item_name = serializers.SerializerMethodField()
    item_type = serializers.SerializerMethodField()
    
    class Meta:
        model = PriceData
        fields = [
            'id', 'material', 'machinery', 'supplier', 'supplier_name',
            'price', 'unit', 'rental_price_daily', 'rental_price_weekly',
            'in_stock', 'stock_quantity', 'location', 'postcode',
            'source_url', 'sku', 'item_name', 'item_type',
            'is_active', 'scraped_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'scraped_at', 'created_at', 'updated_at')
    
    def get_item_name(self, obj):
        item = obj.get_item()
        return item.name if item else None
    
    def get_item_type(self, obj):
        if obj.material:
            return 'material'
        elif obj.machinery:
            return 'machinery'
        return None


class PriceAlertSerializer(serializers.ModelSerializer):
    item_name = serializers.SerializerMethodField()
    item_type = serializers.SerializerMethodField()
    
    class Meta:
        model = PriceAlert
        fields = [
            'id', 'user', 'material', 'machinery', 'alert_type',
            'threshold_price', 'location', 'is_active', 'last_triggered',
            'item_name', 'item_type', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'user', 'last_triggered', 'created_at', 'updated_at')
    
    def get_item_name(self, obj):
        item = obj.material or obj.machinery
        return item.name if item else None
    
    def get_item_type(self, obj):
        if obj.material:
            return 'material'
        elif obj.machinery:
            return 'machinery'
        return None
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PriceHistorySerializer(serializers.ModelSerializer):
    item_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PriceHistory
        fields = [
            'id', 'material', 'machinery', 'avg_price', 'min_price',
            'max_price', 'location', 'date', 'data_points',
            'item_name', 'created_at'
        ]
        read_only_fields = ('id', 'created_at')
    
    def get_item_name(self, obj):
        item = obj.material or obj.machinery
        return item.name if item else None


class ScrapedDataSerializer(serializers.Serializer):
    """Serializer for receiving scraped data from Scrapy service"""
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    brand = serializers.CharField(required=False, allow_blank=True)
    sku = serializers.CharField(required=False, allow_blank=True)
    unit = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    rental_price_daily = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    rental_price_weekly = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    supplier = serializers.CharField(max_length=200)
    supplier_url = serializers.URLField(required=False, allow_blank=True)
    product_url = serializers.URLField(required=False, allow_blank=True)
    in_stock = serializers.BooleanField(default=True)
    stock_quantity = serializers.IntegerField(required=False)
    location = serializers.CharField(required=False, allow_blank=True)
    specifications = serializers.JSONField(required=False)
    length = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    width = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    height = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    weight = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)


class RealtimePricingSerializer(serializers.Serializer):
    """Serializer for real-time pricing requests"""
    items = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of material/machinery IDs"
    )
    location = serializers.CharField(required=False, allow_blank=True)
    item_type = serializers.ChoiceField(
        choices=['material', 'machinery', 'both'],
        default='both'
    )