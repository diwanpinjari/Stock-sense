from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from .models import StockOperation, StockMoveLine, StockLedger, Product
from .forms import (
    ReceiptCreateForm,
    DeliveryCreateForm,
    TransferCreateForm,
    AdjustmentCreateForm
)
from .services import validate_stock_operation, execute_inventory_adjustment


def index(request):
    """Public landing page."""
    return render(request, 'index.html')


@login_required(login_url='login')
def dashboard(request):
    """Live executive dashboard with real-time SQLite metrics."""
    products = Product.objects.select_related('category').all()
    total_products = products.count()

    low_stock_list = []
    total_inventory_items = 0
    for p in products:
        stock = p.total_available_stock
        total_inventory_items += stock
        if stock <= p.reorder_level:
            low_stock_list.append({
                'product': p,
                'available': stock,
                'reorder_level': p.reorder_level
            })

    pending_receipts = StockOperation.objects.filter(
        operation_type='receipt', status__in=['draft', 'waiting', 'ready']
    ).count()

    pending_deliveries = StockOperation.objects.filter(
        operation_type='delivery', status__in=['draft', 'waiting', 'ready']
    ).count()

    internal_transfers = StockOperation.objects.filter(
        operation_type='internal', status__in=['draft', 'waiting', 'ready']
    ).count()

    recent_ledger = StockLedger.objects.select_related(
        'product', 'source_location', 'destination_location', 'operation'
    ).order_by('-timestamp')[:7]

    context = {
        'total_products': total_products,
        'total_inventory_items': total_inventory_items,
        'low_stock_count': len(low_stock_list),
        'low_stock_list': low_stock_list,
        'pending_receipts': pending_receipts,
        'pending_deliveries': pending_deliveries,
        'internal_transfers': internal_transfers,
        'recent_ledger': recent_ledger,
    }
    return render(request, 'dashboard.html', context)


# ==========================================
# 1. RECEIPTS
# ==========================================

@login_required(login_url='login')
def receipts_list(request):
    receipts = StockOperation.objects.filter(
        operation_type='receipt'
    ).select_related('source_location', 'destination_location').prefetch_related('lines__product').order_by('-created_at')

    return render(request, 'operations/receipts.html', {'receipts': receipts})


@login_required(login_url='login')
def receipt_create(request):
    if request.method == 'POST':
        form = ReceiptCreateForm(request.POST)
        if form.is_valid():
            receipt = StockOperation.objects.create(
                operation_type='receipt',
                source_location=form.cleaned_data['source_location'],
                destination_location=form.cleaned_data['destination_location'],
                status='draft',
                notes=form.cleaned_data['notes'],
                created_by=request.user
            )
            StockMoveLine.objects.create(
                operation=receipt,
                product=form.cleaned_data['product'],
                quantity=form.cleaned_data['quantity']
            )
            messages.success(request, f"Draft receipt {receipt.reference} created successfully!")
            return redirect('receipts_list')
    else:
        form = ReceiptCreateForm()

    return render(request, 'operations/receipt_create.html', {'form': form})


@login_required(login_url='login')
def receipt_validate(request, pk):
    if request.method == 'POST':
        receipt = get_object_or_404(StockOperation, pk=pk, operation_type='receipt')
        try:
            validate_stock_operation(receipt)
            messages.success(request, f"Receipt {receipt.reference} validated! Stock posted to ledger.")
        except ValidationError as e:
            messages.error(request, str(e.message if hasattr(e, 'message') else e))

    return redirect('receipts_list')


# ==========================================
# 2. DELIVERIES
# ==========================================

@login_required(login_url='login')
def deliveries_list(request):
    deliveries = StockOperation.objects.filter(
        operation_type='delivery'
    ).select_related('source_location', 'destination_location').prefetch_related('lines__product').order_by('-created_at')

    return render(request, 'operations/deliveries.html', {'deliveries': deliveries})


@login_required(login_url='login')
def delivery_create(request):
    if request.method == 'POST':
        form = DeliveryCreateForm(request.POST)
        if form.is_valid():
            delivery = StockOperation.objects.create(
                operation_type='delivery',
                source_location=form.cleaned_data['source_location'],
                destination_location=form.cleaned_data['destination_location'],
                status='draft',
                notes=form.cleaned_data['notes'],
                created_by=request.user
            )
            StockMoveLine.objects.create(
                operation=delivery,
                product=form.cleaned_data['product'],
                quantity=form.cleaned_data['quantity']
            )
            messages.success(request, f"Draft delivery order {delivery.reference} created successfully!")
            return redirect('deliveries_list')
    else:
        form = DeliveryCreateForm()

    return render(request, 'operations/delivery_create.html', {'form': form})


@login_required(login_url='login')
def delivery_validate(request, pk):
    if request.method == 'POST':
        delivery = get_object_or_404(StockOperation, pk=pk, operation_type='delivery')
        try:
            validate_stock_operation(delivery)
            messages.success(request, f"Delivery {delivery.reference} validated! Stock deducted and posted to ledger.")
        except ValidationError as e:
            messages.error(request, str(e.message if hasattr(e, 'message') else e))

    return redirect('deliveries_list')


# ==========================================
# 3. INTERNAL TRANSFERS
# ==========================================

@login_required(login_url='login')
def transfers_list(request):
    transfers = StockOperation.objects.filter(
        operation_type='internal'
    ).select_related('source_location', 'destination_location').prefetch_related('lines__product').order_by('-created_at')

    return render(request, 'operations/transfers.html', {'transfers': transfers})


@login_required(login_url='login')
def transfer_create(request):
    if request.method == 'POST':
        form = TransferCreateForm(request.POST)
        if form.is_valid():
            transfer = StockOperation.objects.create(
                operation_type='internal',
                source_location=form.cleaned_data['source_location'],
                destination_location=form.cleaned_data['destination_location'],
                status='draft',
                notes=form.cleaned_data['notes'],
                created_by=request.user
            )
            StockMoveLine.objects.create(
                operation=transfer,
                product=form.cleaned_data['product'],
                quantity=form.cleaned_data['quantity']
            )
            messages.success(request, f"Draft transfer {transfer.reference} created successfully!")
            return redirect('transfers_list')
    else:
        form = TransferCreateForm()

    return render(request, 'operations/transfer_create.html', {'form': form})


@login_required(login_url='login')
def transfer_validate(request, pk):
    if request.method == 'POST':
        transfer = get_object_or_404(StockOperation, pk=pk, operation_type='internal')
        try:
            validate_stock_operation(transfer)
            messages.success(request, f"Transfer {transfer.reference} validated and posted to ledger.")
        except ValidationError as e:
            messages.error(request, str(e.message if hasattr(e, 'message') else e))

    return redirect('transfers_list')


# ==========================================
# 4. STOCK ADJUSTMENTS
# ==========================================

@login_required(login_url='login')
def adjustment_create(request):
    if request.method == 'POST':
        form = AdjustmentCreateForm(request.POST)
        if form.is_valid():
            try:
                op = execute_inventory_adjustment(
                    product=form.cleaned_data['product'],
                    location=form.cleaned_data['location'],
                    counted_qty=form.cleaned_data['counted_quantity'],
                    user=request.user
                )
                messages.success(request, f"Adjustment {op.reference} applied. System stock aligned with physical count.")
                return redirect('dashboard')
            except ValidationError as e:
                messages.error(request, str(e.message if hasattr(e, 'message') else e))
    else:
        form = AdjustmentCreateForm()

    return render(request, 'operations/adjustment_create.html', {'form': form})