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
        return VendorSerializer(Vendor.objects.get(id=obj.vendor.id), many=False).data

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


class CashOrderItemSerializer(ModelSerializer):
    product_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CashOrderItem
        fields = '__all__'

    def get_product_name(self, obj):
        return obj.product.name


class CashOrderSerializer(ModelSerializer):
    seller_name = serializers.SerializerMethodField(read_only=True)
    items = serializers.SerializerMethodField(read_only=False)

    class Meta:
        model = CashOrder
        fields = [
            'id', 'unique_id', 'customer_name', 'sale_by', 'seller_name', 'warranty', 'quantity',
            'total_profit', 'total_amount', 'updated_at', 'created_at', 'items',
        ]

    def get_seller_name(self, obj):
        return obj.sale_by.username

    def get_items(self, obj):
        return CashOrderItemSerializer(CashOrderItem.objects.filter(cash_order=obj.id), many=True).data


class CreditItemSerializer(ModelSerializer):
    class Meta:
        model = CreditItem
        fields = '__all__'


class CreditSerializer(ModelSerializer):
    items = serializers.SerializerMethodField(read_only=False)

    class Meta:
        model = Credit
        fields = '__all__'

    def get_items(self, obj):
        return CreditItemSerializer(CreditItem.objects.filter(credit=obj.id), many=True).data


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
