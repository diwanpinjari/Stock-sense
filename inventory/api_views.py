from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, Q
from django.core.exceptions import ValidationError

from .models import Category, Product, Warehouse, Location, StockOperation, StockLedger
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    StockOperationSerializer,
    StockLedgerSerializer
)
from .services import validate_stock_operation, execute_inventory_adjustment


class DashboardKPIView(APIView):
    """
    Returns real-time KPI metrics for the inventory dashboard:
    - Total physical products in stock
    - Low stock / out of stock count based on reordering rules
    - Pending receipts, deliveries, and internal transfers
    """
    def get(self, request):
        products = Product.objects.all()
        total_products_count = products.count()

        low_stock_count = 0
        for p in products:
            if p.total_available_stock <= p.reorder_level:
                low_stock_count += 1

        pending_receipts = StockOperation.objects.filter(
            operation_type='receipt', status__in=['draft', 'waiting', 'ready']
        ).count()

        pending_deliveries = StockOperation.objects.filter(
            operation_type='delivery', status__in=['draft', 'waiting', 'ready']
        ).count()

        internal_transfers = StockOperation.objects.filter(
            operation_type='internal', status__in=['draft', 'waiting', 'ready']
        ).count()

        return Response({
            'total_products': total_products_count,
            'low_stock_items': low_stock_count,
            'pending_receipts': pending_receipts,
            'pending_deliveries': pending_deliveries,
            'internal_transfers_scheduled': internal_transfers,
        })


class ProductViewSet(viewsets.ModelViewSet):
    """
    Endpoints for listing, filtering, and creating products.
    Supports query parameters: ?search=..., ?category=...
    """
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        category_id = self.request.query_params.get('category')

        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(sku__icontains=search))
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs


class StockOperationViewSet(viewsets.ModelViewSet):
    """
    Endpoints for receipts, delivery orders, internal transfers, and adjustments.
    Supports filtering by: ?type=receipt&status=ready&warehouse=...
    """
    queryset = StockOperation.objects.select_related(
        'source_location', 'destination_location', 'source_location__warehouse'
    ).prefetch_related('lines__product').all().order_by('-created_at')
    serializer_class = StockOperationSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        op_type = self.request.query_params.get('type')
        status_param = self.request.query_params.get('status')
        warehouse_id = self.request.query_params.get('warehouse')

        if op_type:
            qs = qs.filter(operation_type=op_type)
        if status_param:
            qs = qs.filter(status=status_param)
        if warehouse_id:
            qs = qs.filter(
                Q(source_location__warehouse_id=warehouse_id) |
                Q(destination_location__warehouse_id=warehouse_id)
            )
        return qs

    @action(detail=True, methods=['post'])
    def validate_operation(self, request, pk=None):
        """Action endpoint: /api/operations//validate_operation/"""
        operation = self.get_object()
        try:
            validated_op = validate_stock_operation(operation)
            return Response({
                'status': 'success',
                'message': f'Operation {validated_op.reference} successfully validated and posted to ledger.',
                'operation_status': validated_op.status
            })
        except ValidationError as e:
            return Response({'status': 'error', 'message': str(e.message if hasattr(e, 'message') else e)},
                            status=status.HTTP_400_BAD_REQUEST)


class StockLedgerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only audit log of all stock movements.
    """
    queryset = StockLedger.objects.select_related(
        'product', 'source_location', 'destination_location', 'operation'
    ).all()
    serializer_class = StockLedgerSerializer