from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    DashboardKPIView,
    ProductViewSet,
    StockOperationViewSet,
    StockLedgerViewSet
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='api-products')
router.register(r'operations', StockOperationViewSet, basename='api-operations')
router.register(r'ledger', StockLedgerViewSet, basename='api-ledger')

urlpatterns = [
    path('dashboard/kpis/', DashboardKPIView.as_view(), name='api-dashboard-kpis'),
    path('', include(router.urls)),
]