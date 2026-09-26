from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from .models import (
    StockOperation,
    StockMoveLine,
    StockLedger,
    Product,
    Location,
)

from .forms import (
    ReceiptCreateForm,
    DeliveryCreateForm,
    TransferCreateForm,
    AdjustmentCreateForm,
)

from .services import (
    validate_stock_operation,
    execute_inventory_adjustment,
)


# ============================================================
# PUBLIC LANDING PAGE
# ============================================================

def index(request):
    return render(request, "index.html")


# ============================================================
# DASHBOARD
# ============================================================

@login_required(login_url="login")
def dashboard(request):

    products = Product.objects.select_related(
        "category"
    ).all()

    total_products = products.count()

    low_stock_list = []
    total_inventory_items = 0

    for product in products:

        stock = product.total_available_stock

        total_inventory_items += stock

        if stock <= product.reorder_level:

            low_stock_list.append({
                "product": product,
                "available": stock,
                "reorder_level": product.reorder_level,
            })

    pending_receipts = StockOperation.objects.filter(
        operation_type="receipt",
        status__in=["draft", "waiting", "ready"],
    ).count()

    pending_deliveries = StockOperation.objects.filter(
        operation_type="delivery",
        status__in=["draft", "waiting", "ready"],
    ).count()

    internal_transfers = StockOperation.objects.filter(
        operation_type="internal",
        status__in=["draft", "waiting", "ready"],
    ).count()

    recent_ledger = (
        StockLedger.objects
        .select_related(
            "product",
            "source_location",
            "destination_location",
            "operation",
        )
        .order_by("-timestamp")[:7]
    )

    context = {
        "total_products": total_products,
        "total_inventory_items": total_inventory_items,
        "low_stock_count": len(low_stock_list),
        "low_stock_list": low_stock_list,
        "pending_receipts": pending_receipts,
        "pending_deliveries": pending_deliveries,
        "internal_transfers": internal_transfers,
        "recent_ledger": recent_ledger,
    }

    return render(
        request,
        "dashboard.html",
        context,
    )


# ============================================================
# RECEIPTS
# ============================================================

@login_required(login_url="login")
def receipts_list(request):

    receipts = (
        StockOperation.objects
        .filter(operation_type="receipt")
        .select_related(
            "source_location",
            "destination_location",
            "vendor",
        )
        .prefetch_related(
            "lines__product"
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "operations/receipts.html",
        {
            "receipts": receipts,
        },
    )


@login_required(login_url="login")
def receipt_create(request):

    if request.method == "POST":

        form = ReceiptCreateForm(request.POST)

        if form.is_valid():

            vendor = form.cleaned_data["vendor"]

            destination_location = (
                form.cleaned_data["destination_location"]
            )

            product = form.cleaned_data["product"]

            quantity = form.cleaned_data["quantity"]

            notes = form.cleaned_data["notes"]

            # ------------------------------------------------
            # Create a virtual ledger location for the vendor.
            #
            # The actual Vendor record is stored on
            # StockOperation.vendor.
            # ------------------------------------------------

            vendor_location, _ = Location.objects.get_or_create(
                name=f"Vendor: {vendor.name}",
                warehouse=None,
                location_type="vendor",
            )

            # ------------------------------------------------
            # Create receipt
            # ------------------------------------------------

            receipt = StockOperation.objects.create(
                operation_type="receipt",

                source_location=vendor_location,

                destination_location=destination_location,

                vendor=vendor,

                customer=None,

                status="draft",

                notes=notes,

                created_by=request.user,
            )

            # ------------------------------------------------
            # Create receipt product line
            # ------------------------------------------------

            StockMoveLine.objects.create(
                operation=receipt,
                product=product,
                quantity=quantity,
            )

            messages.success(
                request,
                f"Draft receipt {receipt.reference} "
                f"created successfully for {vendor.name}.",
            )

            return redirect("receipts_list")

    else:

        form = ReceiptCreateForm()

    return render(
        request,
        "operations/receipt_create.html",
        {
            "form": form,
        },
    )


@login_required(login_url="login")
def receipt_validate(request, pk):

    if request.method == "POST":

        receipt = get_object_or_404(
            StockOperation,
            pk=pk,
            operation_type="receipt",
        )

        try:

            validate_stock_operation(receipt)

            messages.success(
                request,
                f"Receipt {receipt.reference} validated! "
                f"Stock posted to ledger.",
            )

        except ValidationError as e:

            messages.error(
                request,
                str(
                    e.message
                    if hasattr(e, "message")
                    else e
                ),
            )

    return redirect("receipts_list")


# ============================================================
# DELIVERIES
# ============================================================

@login_required(login_url="login")
def deliveries_list(request):

    deliveries = (
        StockOperation.objects
        .filter(operation_type="delivery")
        .select_related(
            "source_location",
            "destination_location",
            "customer",
        )
        .prefetch_related(
            "lines__product"
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "operations/deliveries.html",
        {
            "deliveries": deliveries,
        },
    )


@login_required(login_url="login")
def delivery_create(request):

    if request.method == "POST":

        form = DeliveryCreateForm(request.POST)

        if form.is_valid():

            customer = form.cleaned_data["customer"]

            source_location = (
                form.cleaned_data["source_location"]
            )

            product = form.cleaned_data["product"]

            quantity = form.cleaned_data["quantity"]

            notes = form.cleaned_data["notes"]

            # ------------------------------------------------
            # Create a virtual ledger location for customer.
            #
            # The actual Customer record is stored on
            # StockOperation.customer.
            # ------------------------------------------------

            customer_location, _ = Location.objects.get_or_create(
                name=f"Customer: {customer.name}",
                warehouse=None,
                location_type="customer",
            )

            # ------------------------------------------------
            # Create delivery
            # ------------------------------------------------

            delivery = StockOperation.objects.create(
                operation_type="delivery",

                source_location=source_location,

                destination_location=customer_location,

                vendor=None,

                customer=customer,

                status="draft",

                notes=notes,

                created_by=request.user,
            )

            # ------------------------------------------------
            # Create delivery product line
            # ------------------------------------------------

            StockMoveLine.objects.create(
                operation=delivery,
                product=product,
                quantity=quantity,
            )

            messages.success(
                request,
                f"Draft delivery {delivery.reference} "
                f"created successfully for {customer.name}.",
            )

            return redirect("deliveries_list")

    else:

        form = DeliveryCreateForm()

    return render(
        request,
        "operations/delivery_create.html",
        {
            "form": form,
        },
    )


@login_required(login_url="login")
def delivery_validate(request, pk):

    if request.method == "POST":

        delivery = get_object_or_404(
            StockOperation,
            pk=pk,
            operation_type="delivery",
        )

        try:

            validate_stock_operation(delivery)

            messages.success(
                request,
                f"Delivery {delivery.reference} validated! "
                f"Stock deducted and posted to ledger.",
            )

        except ValidationError as e:

            messages.error(
                request,
                str(
                    e.message
                    if hasattr(e, "message")
                    else e
                ),
            )

    return redirect("deliveries_list")


# ============================================================
# INTERNAL TRANSFERS
# ============================================================

@login_required(login_url="login")
def transfers_list(request):

    transfers = (
        StockOperation.objects
        .filter(operation_type="internal")
        .select_related(
            "source_location",
            "destination_location",
        )
        .prefetch_related(
            "lines__product"
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "operations/transfers.html",
        {
            "transfers": transfers,
        },
    )


@login_required(login_url="login")
def transfer_create(request):

    if request.method == "POST":

        form = TransferCreateForm(request.POST)

        if form.is_valid():

            transfer = StockOperation.objects.create(
                operation_type="internal",

                source_location=(
                    form.cleaned_data["source_location"]
                ),

                destination_location=(
                    form.cleaned_data["destination_location"]
                ),

                status="draft",

                notes=form.cleaned_data["notes"],

                created_by=request.user,
            )

            StockMoveLine.objects.create(
                operation=transfer,
                product=form.cleaned_data["product"],
                quantity=form.cleaned_data["quantity"],
            )

            messages.success(
                request,
                f"Draft transfer {transfer.reference} "
                f"created successfully!",
            )

            return redirect("transfers_list")

    else:

        form = TransferCreateForm()

    return render(
        request,
        "operations/transfer_create.html",
        {
            "form": form,
        },
    )


@login_required(login_url="login")
def transfer_validate(request, pk):

    if request.method == "POST":

        transfer = get_object_or_404(
            StockOperation,
            pk=pk,
            operation_type="internal",
        )

        try:

            validate_stock_operation(transfer)

            messages.success(
                request,
                f"Transfer {transfer.reference} "
                f"validated and posted to ledger.",
            )

        except ValidationError as e:

            messages.error(
                request,
                str(
                    e.message
                    if hasattr(e, "message")
                    else e
                ),
            )

    return redirect("transfers_list")


# ============================================================
# STOCK ADJUSTMENTS
# ============================================================

@login_required(login_url="login")
def adjustment_create(request):

    if request.method == "POST":

        form = AdjustmentCreateForm(request.POST)

        if form.is_valid():

            try:

                operation = execute_inventory_adjustment(
                    product=form.cleaned_data["product"],

                    location=form.cleaned_data["location"],

                    counted_qty=(
                        form.cleaned_data["counted_quantity"]
                    ),

                    user=request.user,
                )

                messages.success(
                    request,
                    f"Adjustment {operation.reference} "
                    f"applied. System stock aligned "
                    f"with physical count.",
                )

                return redirect("dashboard")

            except ValidationError as e:

                messages.error(
                    request,
                    str(
                        e.message
                        if hasattr(e, "message")
                        else e
                    ),
                )

    else:

        form = AdjustmentCreateForm()

    return render(
        request,
        "operations/adjustment_create.html",
        {
            "form": form,
        },
    )