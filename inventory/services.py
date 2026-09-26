from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Sum
from .models import StockOperation, StockLedger, Location, Product


def get_product_stock_at_location(product: Product, location: Location) -> Decimal:
    """
    Calculates physical stock for a product at a specific location
    by querying the immutable StockLedger.
    """
    incoming = StockLedger.objects.filter(
        product=product,
        destination_location=location
    ).aggregate(Sum('quantity'))['quantity__sum'] or Decimal('0.00')

    outgoing = StockLedger.objects.filter(
        product=product,
        source_location=location
    ).aggregate(Sum('quantity'))['quantity__sum'] or Decimal('0.00')

    return incoming - outgoing


@transaction.atomic
def validate_stock_operation(operation: StockOperation) -> StockOperation:
    """
    Validates and executes an inventory operation:
    1. Locks row to prevent duplicate validation.
    2. Validates status is not already done/canceled.
    3. Checks sufficient stock for outgoing moves (delivery/internal).
    4. Writes ledger entries and sets status to 'done'.
    """
    op = StockOperation.objects.select_for_update().get(pk=operation.pk)

    if op.status in ['done', 'canceled']:
        raise ValidationError(f"Operation {op.reference} is already {op.status} and cannot be validated.")

    move_lines = op.lines.select_related('product').all()
    if not move_lines.exists():
        raise ValidationError(f"Operation {op.reference} contains no product lines to validate.")

    if op.operation_type in ['delivery', 'internal']:
        for line in move_lines:
            available_qty = get_product_stock_at_location(line.product, op.source_location)
            if available_qty < line.quantity:
                raise ValidationError(
                    f"Insufficient stock for {line.product.name} (SKU: {line.product.sku}) "
                    f"at location '{op.source_location}'. Available: {available_qty}, Required: {line.quantity}"
                )

    for line in move_lines:
        StockLedger.objects.create(
            operation=op,
            product=line.product,
            source_location=op.source_location,
            destination_location=op.destination_location,
            quantity=line.quantity
        )

    op.status = 'done'
    op.save()
    return op


@transaction.atomic
def execute_inventory_adjustment(product: Product, location: Location, counted_qty: Decimal, user=None) -> StockOperation:
    """
    Reconciles physical count differences with system records:
    - If counted > current, moves surplus from 'inventory_loss' into stock.
    - If counted < current, moves deficit from stock into 'inventory_loss'.
    """
    current_qty = get_product_stock_at_location(product, location)
    difference = Decimal(str(counted_qty)) - current_qty

    if difference == 0:
        raise ValidationError(f"Counted quantity matches current recorded stock ({current_qty}). No adjustment needed.")

    loss_location, _ = Location.objects.get_or_create(
        location_type='inventory_loss',
        defaults={'name': 'Inventory Adjustment / Loss'}
    )

    if difference > 0:
        src_loc = loss_location
        dest_loc = location
        adj_qty = difference
    else:
        src_loc = location
        dest_loc = loss_location
        adj_qty = abs(difference)

    adjustment_op = StockOperation.objects.create(
        operation_type='adjustment',
        source_location=src_loc,
        destination_location=dest_loc,
        status='draft',
        created_by=user,
        notes=f"Auto-adjustment: Recorded={current_qty}, Counted={counted_qty}"
    )

    adjustment_op.lines.create(product=product, quantity=adj_qty)
    return validate_stock_operation(adjustment_op)