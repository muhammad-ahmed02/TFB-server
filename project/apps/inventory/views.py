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
    queryset = CashOrder.objects.all().order_by('-updated_at')
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = [
        'unique_id', 'product__name', 'created_at', 'updated_at', 'imei_number__number', 'sale_by__username'
    ]

    def create(self, request, *args, **kwargs):
        seller = SellerProfile.objects.get(id=request.data['sale_by'])
        product = Products.objects.get(id=request.data['product'])

        cash_order = CashOrder.objects.create(
            customer_name=request.data['customer_name'],
            product=product,
            sale_by=seller,
            sale_price=request.data['sale_price'],
            warranty=request.data['warranty'],
            imei_number=IMEINumber.objects.get(number=request.data['imei_number']),
        )
        Transaction.objects.create(
            order=cash_order,
            seller=seller,
            company=CompanyProfile.objects.get()
        )
        return Response(self.serializer_class(cash_order, many=False).data)


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
        try:
            start_date = self.request.query_params['start']
            end_date = self.request.query_params['end']
            return CashOrder.objects.filter(created_at__range=[start_date, end_date])
        except Exception as e:
            print(e)
            return {}

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        content = io.BytesIO()
        row = "{unique_id}, {product_name}, {sale_price}, {cost_price}, {total_profit}, {sale_by}, {seller_profit}, " \
              "{owner_profit}, {business_profit}, {warranty}, {date}\n"
        content.write(
            row.format(
                unique_id="Unique ID",
                product_name="Product Name",
                sale_price="Sale Price",
                cost_price="Cost Price",
                total_profit="Total Profit",
                sale_by="Sale By",
                seller_profit="Seller Profit",
                owner_profit="Owner Profit",
                business_profit="Business Profit",
                warranty="Warranty",
                date="Date"
            ).encode("utf-8")
        )

        total_business = 0
        total_profit = 0

        for order in queryset:
            transaction = Transaction.objects.get(order=order.id)
            total_business += order.sale_price
            total_profit += transaction.total_profit

            content.write(
                row.format(
                    unique_id=order.unique_id,
                    product_name=order.product.name,
                    sale_price=order.sale_price,
                    cost_price=order.product.purchasing_price,
                    total_profit=transaction.total_profit,
                    sale_by=order.sale_by.username,
                    seller_profit=transaction.seller_profit,
                    owner_profit=transaction.owner_profit,
                    business_profit=transaction.business_profit,
                    warranty=f"{order.warranty} Days",
                    date=order.created_at.strftime("%d-%m-%Y %H:%M:%S")
                ).encode("utf-8")
            )

        total_row = "\n{total_business}, {total_profit}\n"
        content.write(
            total_row.format(
                total_business="Total Business",
                total_profit="Total Profit",
            ).encode("utf-8")
        )
        content.write(
            total_row.format(
                total_business=f"PKR {total_business}",
                total_profit=f"PKR {total_profit}",
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
        try:
            start_date = self.request.query_params['start']
            end_date = self.request.query_params['end']
            return ReturnCashOrder.objects.filter(created_at__range=[start_date, end_date])
        except Exception as e:
            print(e)
            return {}

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

        pdf = html_to_pdf("inventory/temp.html")
        return HttpResponse(pdf, content_type="application/pdf")


class CompanyProfileViewSet(ModelViewSet):
    serializer_class = CompanyProfileSerializer
    queryset = CompanyProfile.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None
    http_method_names = ['get', 'put', 'patch']
