from django.contrib import admin
from django.urls import path, include

from inventory import views, views_auth


urlpatterns = [
    # =========================================================
    # ADMIN
    # =========================================================
    path("admin/", admin.site.urls),

    # =========================================================
    # API
    # =========================================================
    path("api/", include("inventory.api_urls")),

    # =========================================================
    # PUBLIC LANDING PAGE
    # =========================================================
    path("", views.index, name="index"),

    # =========================================================
    # REGISTRATION + OTP
    # =========================================================
    path(
        "register/",
        views_auth.user_register,
        name="register",
    ),

    path(
        "register/verify/",
        views_auth.register_verify,
        name="register_verify",
    ),

    path(
        "register/resend-otp/",
        views_auth.register_resend_otp,
        name="register_resend_otp",
    ),

    # =========================================================
    # AUTHENTICATION
    # =========================================================
    path(
        "login/",
        views_auth.user_login,
        name="login",
    ),

    path(
        "logout/",
        views_auth.user_logout,
        name="logout",
    ),

    # Password reset request
    path(
        "forgot-password/",
        views_auth.password_reset_request,
        name="forgot_password",
    ),

    # Password reset OTP confirmation
    path(
        "reset-password/",
        views_auth.password_reset_confirm,
        name="reset_password",
    ),

    # =========================================================
    # DASHBOARD
    # =========================================================
    path(
        "dashboard/",
        views.dashboard,
        name="dashboard",
    ),

    # =========================================================
    # RECEIPTS
    # =========================================================
    path(
        "receipts/",
        views.receipts_list,
        name="receipts_list",
    ),

    path(
        "receipts/new/",
        views.receipt_create,
        name="receipt_create",
    ),

    path(
        "receipts/<int:pk>/validate/",
        views.receipt_validate,
        name="receipt_validate",
    ),

    # =========================================================
    # DELIVERIES
    # =========================================================
    path(
        "deliveries/",
        views.deliveries_list,
        name="deliveries_list",
    ),

    path(
        "deliveries/new/",
        views.delivery_create,
        name="delivery_create",
    ),

    path(
        "deliveries/<int:pk>/validate/",
        views.delivery_validate,
        name="delivery_validate",
    ),

    # =========================================================
    # INTERNAL TRANSFERS
    # =========================================================
    path(
        "transfers/",
        views.transfers_list,
        name="transfers_list",
    ),

    path(
        "transfers/new/",
        views.transfer_create,
        name="transfer_create",
    ),

    path(
        "transfers/<int:pk>/validate/",
        views.transfer_validate,
        name="transfer_validate",
    ),

    # =========================================================
    # STOCK ADJUSTMENTS
    # =========================================================
    path(
        "adjustments/new/",
        views.adjustment_create,
        name="adjustment_create",
    ),
]