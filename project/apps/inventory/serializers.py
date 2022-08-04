from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import *


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__'


class SellerProfileSerializer(ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = '__all__'


class SettingSerializer(ModelSerializer):
    class Meta:
        model = Setting
        fields = '__all__'


class CashOrderSerializer(ModelSerializer):
    product_detail = serializers.SerializerMethodField(read_only=True)
    seller_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CashOrder
        fields = '__all__'

    def get_product_detail(self, obj):
        try:
            return ProductSerializer(Products.objects.filter(id=obj.product.id), many=True).data
        except Exception as e:
            print(e)
            return {}

    def get_seller_name(self, obj):
        return obj.sale_by.user.username
