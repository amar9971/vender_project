from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VendorViewSet, PurchaseOrderViewSet, HistoricalPerformanceViewSet
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView, TokenVerifyView

router = DefaultRouter()
router.register(r'vendors', VendorViewSet)
router.register(r'purchase_orders', PurchaseOrderViewSet)
router.register(r'purchase_orders', HistoricalPerformanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
