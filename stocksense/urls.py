from django.contrib import admin
from django.urls import path, include
from inventory import views, views_auth

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('inventory.api_urls')),

    # Public Landing
    path('', views.index, name='index'),

    # Registration with OTP
    path('register/', views_auth.user_register, name='register'),
    path('register/verify/', views_auth.register_verify, name='register_verify'),
    path('register/resend-otp/', views_auth.register_resend_otp, name='register_resend_otp'),

    # Authentication
    path('login/', views_auth.user_login, name='login'),
    path('logout/', views_auth.user_logout, name='logout'),
    path('forgot-password/', views_auth.password_reset_request, name='password_reset_request'),
    path('reset-password/', views_auth.password_reset_confirm, name='password_reset_confirm'),

    # Executive Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Operations
    path('receipts/', views.receipts_list, name='receipts_list'),
    path('receipts/new/', views.receipt_create, name='receipt_create'),
    path('receipts//validate/', views.receipt_validate, name='receipt_validate'),

    path('deliveries/', views.deliveries_list, name='deliveries_list'),
    path('deliveries/new/', views.delivery_create, name='delivery_create'),
    path('deliveries//validate/', views.delivery_validate, name='delivery_validate'),

    path('transfers/', views.transfers_list, name='transfers_list'),
    path('transfers/new/', views.transfer_create, name='transfer_create'),
    path('transfers//validate/', views.transfer_validate, name='transfer_validate'),

    path('adjustments/new/', views.adjustment_create, name='adjustment_create'),
]