from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import ProductViewSet

router = SimpleRouter()

router.register(r"products", ProductViewSet, basename="All Products")

urlpatterns = router.urls
