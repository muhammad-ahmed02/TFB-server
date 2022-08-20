from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import *


class IMEISerializer(ModelSerializer):
    class Meta:
        model = IMEINumber
        fields = [
            'number'
        ]


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class VendorSerializer(ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'


class ProductStockInSerializer(ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    vendor = serializers.SerializerMethodField(read_only=True)

    def get_name(self, obj):
        return obj.product.name

    def get_vendor(self, obj):
        return obj.vendor.name

    class Meta:
        model = ProductStockIn
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
            return ProductSerializer(ProductStockIn.objects.filter(id=obj.product_stock.id), many=True).data
        except Exception as e:
            print(e)
            return {}

    def get_seller_name(self, obj):
        return obj.sale_by.username


class ReturnCashOrderSerializer(ModelSerializer):
    cashorder_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ReturnCashOrder
        fields = '__all__'

    def get_cashorder_detail(self, obj):
        try:
            return CashOrderSerializer(CashOrder.objects.filter(id=obj.cash_order.id), many=True).data
        except Exception as e:
            print(e)
            return {}


class CompanyProfileSerializer(ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = "__all__"
