from django.contrib import admin
from .models import Category, Product, Warehouse, Location, StockOperation, StockMoveLine, StockLedger


class StockMoveLineInline(admin.TabularInline):
    model = StockMoveLine
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'uom', 'reorder_level', 'total_available_stock')
    search_fields = ('name', 'sku')
    list_filter = ('category', 'uom')


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse', 'location_type')
    list_filter = ('location_type', 'warehouse')


@admin.register(StockOperation)
class StockOperationAdmin(admin.ModelAdmin):
    list_display = ('reference', 'operation_type', 'source_location', 'destination_location', 'status', 'scheduled_date')
    list_filter = ('operation_type', 'status', 'scheduled_date')
    inlines = [StockMoveLineInline]


@admin.register(StockLedger)
class StockLedgerAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'operation', 'product', 'source_location', 'destination_location', 'quantity')
    list_filter = ('product', 'timestamp')
    readonly_fields = ('operation', 'product', 'source_location', 'destination_location', 'quantity', 'timestamp')

    def has_add_permission(self, request):
        return False  # StockLedger entries must be created via operations, never manually typed


admin.site.register(Category)