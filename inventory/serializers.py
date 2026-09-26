from rest_framework import serializers
from .models import Category, Product, Warehouse, Location, StockOperation, StockMoveLine, StockLedger


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    total_available_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category', 'category_name',
            'uom', 'reorder_level', 'total_available_stock',
            'created_at', 'updated_at'
        ]

    def validate_sku(self, value):
        """SKU must be stored uppercase with no spaces."""
        cleaned_sku = value.strip().upper()
        if ' ' in cleaned_sku:
            raise serializers.ValidationError("SKU must not contain spaces.")
        return cleaned_sku


class StockMoveLineSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_sku = serializers.ReadOnlyField(source='product.sku')

    class Meta:
        model = StockMoveLine
        fields = ['id', 'product', 'product_name', 'product_sku', 'quantity']


class StockOperationSerializer(serializers.ModelSerializer):
    lines = StockMoveLineSerializer(many=True, read_only=True)
    source_location_name = serializers.ReadOnlyField(source='source_location.__str__')
    destination_location_name = serializers.ReadOnlyField(source='destination_location.__str__')
    operation_type_display = serializers.CharField(source='get_operation_type_display', read_only=True)

    class Meta:
        model = StockOperation
        fields = [
            'id', 'reference', 'operation_type', 'operation_type_display',
            'source_location', 'source_location_name',
            'destination_location', 'destination_location_name',
            'status', 'scheduled_date', 'notes', 'lines', 'created_at'
        ]
        read_only_fields = ['reference', 'status', 'created_at']


class StockLedgerSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_sku = serializers.ReadOnlyField(source='product.sku')
    source_location_name = serializers.ReadOnlyField(source='source_location.__str__')
    destination_location_name = serializers.ReadOnlyField(source='destination_location.__str__')
    operation_ref = serializers.ReadOnlyField(source='operation.reference')

    class Meta:
        model = StockLedger
        fields = [
            'id', 'timestamp', 'operation_ref', 'product_name',
            'product_sku', 'source_location_name', 'destination_location_name', 'quantity'
        ]