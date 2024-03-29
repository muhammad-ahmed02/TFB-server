from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import *

router = SimpleRouter()

router.register(r"products", ProductViewSet, basename="Products")
router.register(r"vendor", VendorViewSet, basename="Vendors")
router.register(r"products-stock", ProductStockInViewSet, basename="Product Stock")
router.register(r"settings", SettingViewSet, basename="Settings")
router.register(r"cashorder", CashOrderViewSet, basename="CashOrder")
# router.register(r"cashorder-items", CashOrderItemViewSet, basename="CashOrder Items")
router.register(r"return-cashorder", ReturnCashOrderViewSet, basename="Return CashOrder")
router.register(r"seller-profile", SellerProfileViewSet, basename="Sellers")
router.register(r"imei-numbers", IMEIViewSet, basename="IMEIs")
router.register(r"company-profile", CompanyProfileViewSet, basename="Company profile")
router.register(r"credit", CreditViewSet, basename="Credit")
router.register(r"claim", ClaimViewSet, basename="Claim")

urlpatterns = [
    path('export/cashorder/', ExportCashOrderViews.as_view()),
    path('export/return-cashorder/', ExportReturnCashOrderViews.as_view()),
    path('export/cashorder/invoice/<str:unique_id>', GenerateOrderInvoice.as_view()),
    path('available-imei/', AvailableImeiViews.as_view()),
    path("export/week-closure/", ExportWeekClosureView.as_view()),
    path("week-closure/", WeekClosureViews.as_view()),
    path("check-valid-imei/", check_valid_imei),
] + router.urls
