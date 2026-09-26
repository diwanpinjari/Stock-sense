from django.contrib import admin
from django.urls import path, include
from inventory import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('inventory.api_urls')),

    # Core Operations (Pure Dynamic Django Views)
    path('', views.receipts_list, name='receipts_list'),
    path('receipts/new/', views.receipt_create, name='receipt_create'),
    path('receipts//validate/', views.receipt_validate, name='receipt_validate'),
]