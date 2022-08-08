from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django.http import FileResponse
from datetime import datetime
import io

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


class ReturnCashOrderViewSet(ModelViewSet):
    serializer_class = ReturnCashOrderSerializer
    queryset = ReturnCashOrder.objects.all()
    permission_classes = [IsAuthenticated]


class ExportCashOrderViews(ListAPIView):
    pagination_class = None
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    queryset = CashOrder.objects.all()
    search_fields = ['unique_id']

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        content = io.BytesIO()
        row = "{unique_id}, {product_name}, {sale_price}, {cost_price}, {sale_by}, {profit}, {warranty}, " \
              "{date}\n "
        content.write(
            row.format(
                unique_id="Unique ID",
                product_name="Product Name",
                sale_price="Sale Price",
                cost_price="Cost Price",
                sale_by="Sale By",
                profit="Profit",
                warranty="Warranty",
                date="Date"
            ).encode("utf-8")
        )
        for order in queryset:
            content.write(
                row.format(
                    unique_id=order.unique_id,
                    product_name=order.product.name,
                    sale_price=order.sale_price,
                    cost_price=order.product.purchasing_price,
                    sale_by=order.sale_by.username,
                    profit=order.profit,
                    warranty=f"{order.warranty} Days",
                    date=order.created_at.strftime("%d-%m-%Y %H:%M:%S")
                ).encode("utf-8")
            )
        content.seek(0)
        return FileResponse(
            content, as_attachment=True, filename='CashOrderReport.csv'
        )


class ExportReturnCashOrderViews(ListAPIView):
    pagination_class = None
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    queryset = ReturnCashOrder.objects.all()
    search_fields = ['cash_order__unique_id']

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        content = io.BytesIO()
        row = "{unique_id}, {product_name}, {sale_price}, {sale_by}, {reason}, {return_amount}, {date} \n"

        content.write(
            row.format(
                unique_id="Cash Order Unique ID",
                product_name="Product Name",
                sale_price="Sale Price",
                sale_by="Sale By",
                reason="Reason",
                return_amount="Return Amount",
                date="Date"
            ).encode("utf-8")
        )
        for order in queryset:
            content.write(
                row.format(
                    unique_id=order.cash_order.unique_id,
                    product_name=order.cash_order.product.name,
                    sale_price=order.cash_order.sale_price,
                    sale_by=order.cash_order.sale_by.username,
                    reason=order.reason,
                    return_amount=order.return_amount,
                    date=order.created_at.strftime("%d-%m-%Y %H:%M:%S")
                ).encode("utf-8")
            )

        content.seek(0)
        return FileResponse(
            content, as_attachment=True, filename='ReturnCashOrderReport.csv'
        )
