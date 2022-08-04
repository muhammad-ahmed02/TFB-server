from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters

from .serializers import *


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Products.objects.all().order_by('-created_at')
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class SellerProfileViewSet(ModelViewSet):
    serializer_class = SellerProfileSerializer
    queryset = SellerProfile.objects.all().order_by('-updated_at')
    permission_classes = [IsAuthenticated]


class SettingViewSet(ModelViewSet):
    serializer_class = SettingSerializer
    queryset = Setting.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None
    http_method_names = ['get', 'put', 'patch']


class CashOrderViewSet(ModelViewSet):
    serializer_class = CashOrderSerializer
    queryset = CashOrder.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = ['unique_id']
