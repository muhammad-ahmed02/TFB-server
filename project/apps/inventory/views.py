from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import filters
from django.http import FileResponse, HttpResponse
from django.db import transaction
from django.views import View
from django.template.loader import get_template
from datetime import datetime, timedelta
import io

from .serializers import *
from .utils import html_to_pdf


class IMEIViewSet(ModelViewSet):
    serializer_class = IMEISerializer
    queryset = IMEINumber.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = ['number']


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Products.objects.all().order_by('-created_at')
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """ Provides an API to modify multiple products at once. """
        products = []
        with transaction.atomic():
            for entry in request.data:
                product = Products.objects.get(pk=entry['id'])
                products.append(product)
                product.purchasing_price = entry['purchasing_price']
                product.available_stock = entry['available_stock']
                product.save()
            for schedule in products:
                schedule.clean()
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        IMEIs = request.data['imei_or_serial_number']
        post_IMEIs = []
        for imei in IMEIs:
            try:
                post_IMEIs.append(IMEINumber.objects.get(number=imei).number)
            except Exception as e:
                new_imei = IMEINumber.objects.create(number=imei)
                post_IMEIs.append(new_imei.number)
        product = Products.objects.create(name=request.data['name'],
                                          purchasing_price=request.data['purchasing_price'],
                                          available_stock=request.data['available_stock'],
                                          )
        product.imei_or_serial_number.set(post_IMEIs)
        return Response(self.serializer_class(product, many=False).data)

    def update(self, request, *args, **kwargs):
        product_id = request.data['id']
        IMEIs = request.data['imei_or_serial_number']
        post_IMEIs = []
        for imei in IMEIs:
            try:
                imei_object = IMEINumber.objects.get(number=imei)
                imei_object.number = imei
                imei_object.save()
                post_IMEIs.append(imei_object.number)
            except Exception as e:
                new_imei = IMEINumber.objects.create(number=imei)
                post_IMEIs.append(new_imei.number)
        product = Products.objects.get(id=product_id)
        product.name = request.data['name']
        product.number_of_items_saled = request.data['number_of_items_saled']
        product.available_stock = request.data['available_stock']
        product.purchasing_price = request.data['purchasing_price']
        product.updated_at = request.data['updated_at']
        product.imei_or_serial_number.set(post_IMEIs)
        product.save()
        return Response(self.serializer_class(product, many=False).data)


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

    def get_queryset(self):
        if "date" in self.request.query_params:
            if self.request.query_params['date'] == "today":
                today = datetime.today()
                start_date = today - timedelta(days=1)
                return CashOrder.objects.filter(created_at__range=[start_date, today])
            elif self.request.query_params['date'] == "month":
                current_month = datetime.today().month
                current_year = datetime.today().year
                start_date = datetime(current_year, current_month, 1)
                end_date = datetime(current_year, current_month, 31)
                return CashOrder.objects.filter(created_at__range=[start_date, end_date])
        return CashOrder.objects.all()

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

    def get_queryset(self):
        if "date" in self.request.query_params:
            if self.request.query_params['date'] == "today":
                today = datetime.today()
                start_date = today - timedelta(days=1)
                return ReturnCashOrder.objects.filter(created_at__range=[start_date, today])
            elif self.request.query_params['date'] == "month":
                current_month = datetime.today().month
                current_year = datetime.today().year
                start_date = datetime(current_year, current_month, 1)
                end_date = datetime(current_year, current_month, 31)
                return ReturnCashOrder.objects.filter(created_at__range=[start_date, end_date])
        return ReturnCashOrder.objects.all()

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


class GenerateOrderInvoice(View):
    def get(self, request, unique_id):
        cash_order = CashOrder.objects.get(unique_id=unique_id)

        html = get_template("inventory/company_invoice.html")
        context = {'cash_order': cash_order}
        html_content = html.render(context)
        with open("project/templates/inventory/temp.html", "w") as file:
            file.write(html_content)
            # render_to_string(
            #     "inventory/company_invoice.html", {
            #         "cash_order": cash_order
            #     }

        pdf = html_to_pdf("inventory/temp.html")
        return HttpResponse(pdf, content_type="application/pdf")


class CompanyProfileViewSet(ModelViewSet):
    serializer_class = CompanyProfileSerializer
    queryset = CompanyProfile.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None
    http_method_names = ['get', 'put', 'patch']
