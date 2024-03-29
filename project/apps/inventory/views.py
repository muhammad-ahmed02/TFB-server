from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import filters, status
from rest_framework.views import APIView
from django.http import FileResponse, HttpResponse
from django.db import transaction
from django.views import View
from django.template.loader import get_template
import datetime
import io
import csv

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

    def update(self, request, *args, **kwargs):
        seller = SellerProfile.objects.get(id=request.data['id'])
        prev_business_share = seller.business_share
        new_business_share = request.data['business_share']
        company = CompanyProfile.objects.get()
        seller.profit = 0
        seller.seller_share = request.data['seller_share']
        seller.business_share = new_business_share

        try:
            transactions = Transaction.objects.filter(seller=seller)
            for transaction in transactions:
                cash_order_items = CashOrderItem.objects.filter(cash_order=transaction.order.id)
                for cash_order_item in cash_order_items:
                    product_stock = ProductStockIn.objects.get(id=cash_order_item.product_stock.id)
                    cost_price = product_stock.purchasing_price
                    sale_price = cash_order_item.price
                    total_profit = sale_price - cost_price
                    seller_profit = (total_profit * request.data['seller_share']) / 100
                    seller.profit += seller_profit
                    # deducting business profit for previous business share
                    prev_business_profit = (total_profit * prev_business_share) / 100
                    company.business_balance -= prev_business_profit
                    # adding business profit for new business share
                    new_business_profit = (total_profit * new_business_share) / 100
                    company.business_balance += new_business_profit
            company.save()
            seller.save()
            return Response(self.serializer_class(seller, many=False).data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(data="Error found, {}".format(e), status=status.HTTP_400_BAD_REQUEST)


class SettingViewSet(ModelViewSet):
    serializer_class = SettingSerializer
    queryset = Setting.objects.all()
    permission_classes = [IsAuthenticated]
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

    def destroy(self, request, *args, **kwargs):
        cash_order = CashOrder.objects.get(id=kwargs['pk'])
        cash_order_items = CashOrderItem.objects.filter(cash_order=cash_order.id)
        transactions = Transaction.objects.filter(order=cash_order.id)
        for cash_order_item in cash_order_items:
            product_stock = ProductStockIn.objects.get(id=cash_order_item.product_stock.id)
            product_stock.available_stock += 1
            product_stock.save()

        for transaction in transactions:
            seller = SellerProfile.objects.get(id=transaction.seller.id)
            company = CompanyProfile.objects.get(id=transaction.company.id)
            seller.profit -= transaction.seller_profit
            seller.save()
            company.owner_balance -= transaction.owner_profit
            company.business_balance -= transaction.business_profit
            company.save()
            transaction.delete()

        cash_order.delete()
        return Response(self.serializer_class(cash_order, many=False).data)

    def update(self, request, *args, **kwargs):
        data = "Method not allowed"
        return Response(data, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CreditViewSet(ModelViewSet):
    serializer_class = CreditSerializer
    queryset = Credit.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        items = request.data['items']

        credit = Credit.objects.create(payment_status=request.data['payment_status'])
        for item in items:
            imei_number = IMEINumber.objects.get(number=item['imei_or_serial_number'])
            product_stock = item['product_stock']
            price = item['price']

            CreditItem.objects.create(credit=credit,
                                      price=price,
                                      imei_or_serial_number=imei_number,
                                      product_stock=ProductStockIn.objects.get(id=product_stock))

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

    def destroy(self, request, *args, **kwargs):
        credit = Credit.objects.get(id=kwargs['pk'])
        credit_items = CreditItem.objects.filter(credit=credit.id)
        for credit_item in credit_items:
            product_stock = ProductStockIn.objects.get(id=credit_item.product_stock.id)
            product_stock.available_stock += 1
            if credit.payment_status == "PENDING":
                product_stock.on_credit -= 1
            else:
                product_stock.sold -= 1
            product_stock.save()

        credit.delete()
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
            cash_orders = CashOrder.objects.filter(updated_at__range=[start_date, end_date])
            return cash_orders
        except Exception as e:
            print(e)
            return {}

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report.csv"'
        writer = csv.writer(response)

        total_business = 0
        total_profit = 0

        for order in queryset:
            # cash order basic header
            excluded = ["cashorderitem", "returncashorder", "transaction", "created_at"]
            header = [field.name for field in order._meta.get_fields() if field.name not in excluded]
            writer.writerow(header)
            # writing order basic details
            writer.writerow([getattr(order, field) for field in header])

            total_profit += order.total_profit
            total_business += order.total_amount

            # cash order item header
            item_header = ["item_" + field.name for field in CashOrderItem.objects.first()._meta.get_fields() if field.name != "created_at"]
            writer.writerow(item_header)
            # writing order items data
            for order_item in CashOrderItem.objects.filter(cash_order=order):
                writer.writerow([getattr(order_item, field.replace("item_", "")) for field in item_header])
            writer.writerow([])

        writer.writerow([])
        writer.writerow([])

        writer.writerow(["Total Business", "Total Profit"])
        writer.writerow([total_business, total_profit])
        return response


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
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report.csv"'
        writer = csv.writer(response)

        total_returned_amount = 0

        for return_order in queryset:
            excluded = ["cashorderitem", "returncashorder", "transaction", "created_at"]
            # Return order header
            return_header = [field.name for field in return_order._meta.get_fields() if field.name not in excluded]
            cashorder_excluded = ["cashorderitem", "returncashorder", "transaction",
                                  'id', "unique_id", "created_at", "total_profit"]
            cash_header = list()
            cash_order = CashOrder.objects.get(unique_id=return_order.cash_order)
            for cashorder_field in cash_order._meta.get_fields():
                if cashorder_field.name not in cashorder_excluded:
                    cash_header.append("order_" + cashorder_field.name)
            writer.writerow(return_header + cash_header)
            total_returned_amount += return_order.return_amount
            # writing order basic details
            return_data = [getattr(return_order, field) for field in return_header]
            cash_data = [getattr(cash_order, field.replace("order_", "")) for field in cash_header]
            writer.writerow(return_data + cash_data)
            writer.writerow([])

        writer.writerow([])
        writer.writerow([])

        writer.writerow(["Total Amount Returned"])
        writer.writerow([total_returned_amount])
        return response


class GenerateOrderInvoice(View):
    def get(self, request, unique_id):
        cash_order = CashOrder.objects.get(unique_id=unique_id)
        cash_order_items = CashOrderItem.objects.filter(cash_order=cash_order.id)

        html = get_template("inventory/company_invoice.html")
        context = {'cash_order': cash_order, 'cash_order_items': cash_order_items}
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

    def update(self, request, *args, **kwargs):
        status = request.data['status']
        product_stock = request.data['product_stock']
        imei_or_serial_number = request.data['imei_or_serial_number']
        reason = request.data['reason']
        claim = Claim.objects.get(id=kwargs['pk'])
        claim.status = status
        claim.product_stock = ProductStockIn.objects.get(id=product_stock)
        claim.reason = reason
        claim.imei_or_serial_number = IMEINumber.objects.get(number=imei_or_serial_number)
        claim.save()

        if status == "CLEARED":
            product_stock = ProductStockIn.objects.get(imei_or_serial_number=claim.imei_or_serial_number)
            product_stock.available_stock += 1
            product_stock.on_claim -= 1
            product_stock.save()
        return Response(self.serializer_class(claim, many=False).data)

    def destroy(self, request, *args, **kwargs):
        claim = Claim.objects.get(id=kwargs['pk'])
        product_stock = ProductStockIn.objects.get(id=claim.product_stock.id)
        if claim.status == "PENDING":
            product_stock.on_claim -= 1
            product_stock.available_stock += 1
        else:
            product_stock.on_claim += 1
            product_stock.available_stock -= 1
        product_stock.save()
        claim.delete()
        return Response(self.serializer_class(claim, many=False).data)


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


@api_view(['POST'])
def check_valid_imei(request):
    imei = request.data['imei_or_serial_number']
    if CashOrderItem.objects.filter(imei_or_serial_number=imei).exists():
        return Response(data="False", status=status.HTTP_200_OK)
    else:
        return Response(data="True", status=status.HTTP_200_OK)


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
        return Response(data=WeekClosureSerializer(WeekClosure.objects.all(), many=True).data,
                        status=status.HTTP_200_OK)

    def post(self, request):
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
        return Response(data="Data has been reset", status=status.HTTP_205_RESET_CONTENT)
