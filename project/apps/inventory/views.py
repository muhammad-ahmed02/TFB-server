import datetime

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import filters, status
from rest_framework.views import APIView
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
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]


class VendorViewSet(ModelViewSet):
    serializer_class = VendorSerializer
    queryset = Vendor.objects.all()
    permission_classes = [IsAuthenticated]


class ProductStockInViewSet(ModelViewSet):
    serializer_class = ProductStockInSerializer
    queryset = ProductStockIn.objects.all().order_by('-created_at')
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = ['product__name', 'vendor__name', 'imei_or_serial_number__number', 'id']

    def get_queryset(self):
        if 'available' in self.request.query_params:
            return ProductStockIn.objects.filter(available_stock__gt=0).order_by('-created_at')
        return ProductStockIn.objects.all().order_by('-created_at')

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """ Provides an API to modify multiple products at once. """
        products = []
        with transaction.atomic():
            for entry in request.data:
                product = ProductStockIn.objects.get(pk=entry['id'])
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
            new_imei, found = IMEINumber.objects.get_or_create(number=imei)
            post_IMEIs.append(new_imei.number)
        product = ProductStockIn.objects.create(product=Product.objects.get(id=request.data['product']),
                                                vendor=Vendor.objects.get(id=request.data['vendor']),
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
                print(e)
                new_imei = IMEINumber.objects.create(number=imei)
                post_IMEIs.append(new_imei.number)
        product = ProductStockIn.objects.get(id=product_id)
        product.name = request.data['name']
        product.sold = request.data['sold']
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

    # def update(self, request, *args, **kwargs):
    """
    need to confirm the logic
    should it work with every order ever created or just add/remove the percentage from existing balance
    """


class SettingViewSet(ModelViewSet):
    serializer_class = SettingSerializer
    queryset = Setting.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None
    http_method_names = ['get', 'put', 'patch']


class CashOrderItemViewSet(ModelViewSet):
    serializer_class = CashOrderItemSerializer
    queryset = CashOrderItem.objects.all().order_by('-created_at')
    permission_classes = [IsAuthenticated]


class CashOrderViewSet(ModelViewSet):
    serializer_class = CashOrderSerializer
    queryset = CashOrder.objects.all().order_by('-updated_at')
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = [
        'unique_id', 'created_at', 'updated_at', 'sale_by__username'
    ]

    def create(self, request, *args, **kwargs):
        seller = SellerProfile.objects.get(id=request.data['sale_by'])
        customer_name = request.data['customer_name']
        warranty = request.data['warranty']
        items = request.data['items']

        cash_order = CashOrder.objects.create(
            customer_name=customer_name,
            sale_by=seller,
            warranty=warranty,
        )
        for item in items:
            imei_number = IMEINumber.objects.get(number=item['imei_or_serial_number'])
            CashOrderItem.objects.create(cash_order=cash_order,
                                         price=item['price'],
                                         imei_or_serial_number=imei_number,
                                         product_stock=ProductStockIn.objects.get(id=item['product_stock']))

        return Response(self.serializer_class(cash_order, many=False).data)


class CreditViewSet(ModelViewSet):
    serializer_class = CreditSerializer
    queryset = Credit.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        items = request.data['items']

        credit = Credit.objects.create(payment_status=request.data['payment_status'])
        for item in items:
            imei_number = IMEINumber.objects.get(number=item['imei_or_serial_number'])
            product = item['product']
            price = item['price']

            CreditItem.objects.create(credit=credit,
                                      price=price,
                                      imei_or_serial_number=imei_number,
                                      product=Product.objects.get(id=product))

        return Response(self.serializer_class(credit, many=False).data)

    def update(self, request, *args, **kwargs):
        status = request.data['payment_status']
        credit = Credit.objects.get(id=kwargs['pk'])
        credit.payment_status = status
        credit.save()
        credit_items = CreditItem.objects.filter(credit=credit)

        for item in credit_items:
            product_stock = ProductStockIn.objects.get(imei_or_serial_number=item.imei_or_serial_number.number)

            if status == "PENDING":
                product_stock.on_credit += 1
                product_stock.available_stock -= 1
                product_stock.save()
            else:
                product_stock.on_credit -= 1
                product_stock.sold += 1
                product_stock.save()

        return Response(self.serializer_class(credit, many=False).data)


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
                    product_name=order.product_stock.product.name,
                    sale_price=order.sale_price,
                    cost_price=order.product_stock.purchasing_price,
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


class ClaimViewSet(ModelViewSet):
    serializer_class = ClaimSerializer
    queryset = Claim.objects.all()
    permission_classes = [IsAuthenticated]


class AvailableImeiViews(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = {
            'available_imeis': []
        }
        try:
            product_id = request.query_params['product']
            product = Product.objects.get(id=product_id)
            product_stocks = ProductStockIn.objects.filter(available_stock__gt=0, product=product.id)
            for product_stock in product_stocks:
                for imei in product_stock.imei_or_serial_number.all():
                    data['available_imeis'].append(imei.number)
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(data={"Error, {}".format(e)}, status=status.HTTP_400_BAD_REQUEST)


class ExportWeekClosureView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sellers = SellerProfile.objects.all()
        company = CompanyProfile.objects.get()

        content = io.BytesIO()
        row = "{username}, {profit}, {seller_share}, {business_share}, {updated_at}, {created_at}\n"
        content.write(
            row.format(
                username="Name",
                profit="Profit",
                seller_share="Seller share",
                business_share="Business Share",
                updated_at="Updated Date",
                created_at="Joining Date",
            ).encode("utf-8")
        )

        total_profit = 0

        for seller in sellers:
            total_profit += seller.profit

            content.write(
                row.format(
                    username=seller.username,
                    profit=seller.profit,
                    seller_share=seller.seller_share,
                    business_share=seller.business_share,
                    updated_at=seller.updated_at.strftime("%d-%m-%Y %H:%M:%S"),
                    created_at=seller.created_at.strftime("%d-%m-%Y %H:%M:%S"),
                ).encode("utf-8")
            )

        total_row = "\n{total_profit}, {business_profit}"
        content.write(
            total_row.format(
                total_profit="Total Profit",
                business_profit="Business Profit",
            ).encode("utf-8")
        )
        content.write(
            total_row.format(
                total_profit=f"PKR {total_profit}",
                business_profit=f"PKR {company.business_balance}",
            ).encode("utf-8")
        )

        content.seek(0)

        return FileResponse(
            content, as_attachment=True, filename=f'Week Closure {datetime.date.today()}.csv'
        )


class WeekClosureViews(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sellers = SellerProfile.objects.all()
        total_profit = 0

        for seller in sellers:
            total_profit += seller.profit
            seller.profit = 0
            seller.save()

        company = CompanyProfile.objects.get()

        WeekClosure.objects.create(total_profit=total_profit,
                                   business_profit=company.business_balance)
        company.business_balance = 0
        company.save()
        return Response(data="Data has been reset", status=status.HTTP_200_OK)
