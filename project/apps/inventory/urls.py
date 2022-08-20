from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import *

router = SimpleRouter()

router.register(r"products", ProductViewSet, basename="Products")
router.register(r"vendor", VendorViewSet, basename="Vendors")
router.register(r"products-stock", ProductStockInViewSet, basename="Product Stock")
router.register(r"settings", SettingViewSet, basename="Settings")
router.register(r"cashorder", CashOrderViewSet, basename="CashOrder")
router.register(r"cashorder-items", CashOrderItemViewSet, basename="CashOrder Items")
router.register(r"return-cashorder", ReturnCashOrderViewSet, basename="Return CashOrder")
router.register(r"seller-profile", SellerProfileViewSet, basename="Sellers")
router.register(r"imei-numbers", IMEIViewSet, basename="IMEIs")
router.register(r"company-profile", CompanyProfileViewSet, basename="Company profile")

urlpatterns = [
    path('export/cashorder/', ExportCashOrderViews.as_view()),
    path('export/return-cashorder/', ExportReturnCashOrderViews.as_view()),
    path('export/cashorder/invoice/<str:unique_id>', GenerateOrderInvoice.as_view()),
] + router.urls
