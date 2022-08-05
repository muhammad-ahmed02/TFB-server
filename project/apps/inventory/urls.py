from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import *

router = SimpleRouter()

router.register(r"products", ProductViewSet, basename="Products")
router.register(r"settings", SettingViewSet, basename="Settings")
router.register(r"cashorder", CashOrderViewSet, basename="CashOrder")
router.register(r"return-cashorder", ReturnCashOrderViewSet, basename="Return CashOrder")
router.register(r"seller-profile", SellerProfileViewSet, basename="Sellers")


urlpatterns = router.urls
