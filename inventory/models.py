from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    UOM_CHOICES = [
        ('units', 'Units'),
        ('kg', 'Kilograms (kg)'),
        ('m', 'Meters (m)'),
        ('l', 'Liters (L)'),
        ('boxes', 'Boxes'),
    ]

    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    uom = models.CharField(max_length=20, choices=UOM_CHOICES, default='units')
    reorder_level = models.PositiveIntegerField(default=10, help_text="Minimum stock before low-stock alert triggers")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.sku}] {self.name}"

    @property
    def total_available_stock(self):
        """Calculates current total physical stock across all internal locations."""
        incoming = StockLedger.objects.filter(
            product=self,
            destination_location__location_type='internal'
        ).aggregate(models.Sum('quantity'))['quantity__sum'] or 0

        outgoing = StockLedger.objects.filter(
            product=self,
            source_location__location_type='internal'
        ).aggregate(models.Sum('quantity'))['quantity__sum'] or 0

        return incoming - outgoing


class Warehouse(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Location(models.Model):
    LOCATION_TYPES = [
        ('vendor', 'Vendor (Virtual Incoming)'),
        ('customer', 'Customer (Virtual Outgoing)'),
        ('internal', 'Internal Storage (Physical Warehouse/Rack)'),
        ('inventory_loss', 'Inventory Adjustment / Loss'),
    ]

    name = models.CharField(max_length=100)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True, related_name='locations')
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES, default='internal')

    class Meta:
        unique_together = ('name', 'warehouse')

    def __str__(self):
        if self.warehouse:
            return f"{self.warehouse.code}/{self.name}"
        return self.name


class StockOperation(models.Model):
    OPERATION_TYPES = [
        ('receipt', 'Receipt (Incoming)'),
        ('delivery', 'Delivery Order (Outgoing)'),
        ('internal', 'Internal Transfer'),
        ('adjustment', 'Stock Adjustment'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('waiting', 'Waiting Availability'),
        ('ready', 'Ready'),
        ('done', 'Done'),
        ('canceled', 'Canceled'),
    ]

    reference = models.CharField(max_length=50, unique=True, editable=False)
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES)
    source_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='outgoing_operations')
    destination_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='incoming_operations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            prefix_map = {
                'receipt': 'REC',
                'delivery': 'DEL',
                'internal': 'INT',
                'adjustment': 'ADJ'
            }
            prefix = prefix_map.get(self.operation_type, 'STK')
            count = StockOperation.objects.filter(operation_type=self.operation_type).count() + 1
            self.reference = f"{prefix}/{timezone.now().year}/{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} ({self.get_operation_type_display()}) - {self.status.upper()}"


class StockMoveLine(models.Model):
    operation = models.ForeignKey(StockOperation, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='move_lines')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])

    def __str__(self):
        return f"{self.product.name} - Qty: {self.quantity} ({self.operation.reference})"


class StockLedger(models.Model):
    """
    Immutable ledger of all stock transactions.
    Rows are created strictly when an operation reaches 'Done'.
    """
    operation = models.ForeignKey(StockOperation, on_delete=models.PROTECT, related_name='ledger_entries')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='ledger_records')
    source_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='ledger_source_moves')
    destination_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='ledger_destination_moves')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} | {self.product.sku}: {self.quantity} from {self.source_location} to {self.destination_location}"
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Warehouse Manager (Full System & Approvals)'),
        ('operator', 'Warehouse Operator (Receipts & Shipments)'),
        ('auditor', 'Stock Auditor (Ledger Audits & Discrepancies)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='operator')

    # Explicit manager declaration stops VS Code / Pylance "no objects member" warning
    objects = models.Manager()

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    """Automatically ensure a profile exists when any User is saved."""
    if created:
        role = 'manager' if instance.is_superuser else 'operator'
        UserProfile.objects.get_or_create(user=instance, defaults={'role': role})