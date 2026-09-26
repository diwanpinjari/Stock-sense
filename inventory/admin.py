from django.contrib import admin

from .models import (
    Category,
    Vendor,
    Customer,
    Product,
    Warehouse,
    Location,
    StockOperation,
    StockMoveLine,
    StockLedger,
    UserProfile,
)


# ============================================================
# CATEGORY
# ============================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
    )

    search_fields = (
        "name",
        "description",
    )


# ============================================================
# VENDOR
# ============================================================

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "contact_person",
        "phone",
        "email",
        "tax_number",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "contact_person",
        "phone",
        "email",
        "tax_number",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    ordering = (
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Vendor Information",
            {
                "fields": (
                    "name",
                    "is_active",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "contact_person",
                    "phone",
                    "email",
                    "address",
                )
            },
        ),
        (
            "Tax Information",
            {
                "fields": (
                    "tax_number",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "notes",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )


# ============================================================
# CUSTOMER
# ============================================================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "contact_person",
        "phone",
        "email",
        "tax_number",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "contact_person",
        "phone",
        "email",
        "tax_number",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    ordering = (
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Customer Information",
            {
                "fields": (
                    "name",
                    "is_active",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "contact_person",
                    "phone",
                    "email",
                    "address",
                )
            },
        ),
        (
            "Tax Information",
            {
                "fields": (
                    "tax_number",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "notes",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )


# ============================================================
# PRODUCT
# ============================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "sku",
        "name",
        "category",
        "uom",
        "reorder_level",
        "stock_display",
        "created_at",
    )

    search_fields = (
        "sku",
        "name",
    )

    list_filter = (
        "category",
        "uom",
    )

    ordering = (
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "stock_display",
    )

    fieldsets = (
        (
            "Product Information",
            {
                "fields": (
                    "name",
                    "sku",
                    "category",
                    "uom",
                )
            },
        ),
        (
            "Inventory Settings",
            {
                "fields": (
                    "reorder_level",
                )
            },
        ),
        (
            "Current Stock",
            {
                "fields": (
                    "stock_display",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    @admin.display(
        description="Available Stock"
    )
    def stock_display(self, obj):
        return obj.total_available_stock


# ============================================================
# WAREHOUSE
# ============================================================

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "code",
        "address",
    )

    search_fields = (
        "name",
        "code",
        "address",
    )

    ordering = (
        "name",
    )


# ============================================================
# LOCATION
# ============================================================

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "warehouse",
        "location_type",
    )

    search_fields = (
        "name",
        "warehouse__name",
        "warehouse__code",
    )

    list_filter = (
        "location_type",
        "warehouse",
    )

    ordering = (
        "warehouse",
        "name",
    )


# ============================================================
# STOCK OPERATION
# ============================================================

@admin.register(StockOperation)
class StockOperationAdmin(admin.ModelAdmin):

    list_display = (
        "reference",
        "operation_type",
        "vendor",
        "customer",
        "source_location",
        "destination_location",
        "status",
        "scheduled_date",
        "created_by",
    )

    search_fields = (
        "reference",
        "vendor__name",
        "customer__name",
        "notes",
    )

    list_filter = (
        "operation_type",
        "status",
        "scheduled_date",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "reference",
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "vendor",
        "customer",
        "created_by",
    )

    fieldsets = (
        (
            "Operation",
            {
                "fields": (
                    "reference",
                    "operation_type",
                    "status",
                )
            },
        ),
        (
            "Business Partner",
            {
                "fields": (
                    "vendor",
                    "customer",
                )
            },
        ),
        (
            "Locations",
            {
                "fields": (
                    "source_location",
                    "destination_location",
                )
            },
        ),
        (
            "Schedule",
            {
                "fields": (
                    "scheduled_date",
                    "created_by",
                )
            },
        ),
        (
            "Notes",
            {
                "fields": (
                    "notes",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )


# ============================================================
# STOCK MOVE LINE
# ============================================================

@admin.register(StockMoveLine)
class StockMoveLineAdmin(admin.ModelAdmin):

    list_display = (
        "operation",
        "product",
        "quantity",
    )

    search_fields = (
        "operation__reference",
        "product__name",
        "product__sku",
    )

    list_filter = (
        "product",
    )


# ============================================================
# STOCK LEDGER
# ============================================================

@admin.register(StockLedger)
class StockLedgerAdmin(admin.ModelAdmin):

    list_display = (
        "timestamp",
        "operation",
        "product",
        "quantity",
        "source_location",
        "destination_location",
    )

    search_fields = (
        "operation__reference",
        "product__name",
        "product__sku",
    )

    list_filter = (
        "timestamp",
        "source_location",
        "destination_location",
    )

    ordering = (
        "-timestamp",
    )

    readonly_fields = (
        "operation",
        "product",
        "source_location",
        "destination_location",
        "quantity",
        "timestamp",
    )


# ============================================================
# USER PROFILE
# ============================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "role",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
    )

    list_filter = (
        "role",
    )