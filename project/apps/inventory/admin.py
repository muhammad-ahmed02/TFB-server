from django.contrib import admin
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import format_html
# from weasyprint import HTML

from .models import *


@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'purchasing_price', 'available_stock', 'number_of_items_saled')

    search_fields = ('name', 'purchasing_price', 'available_stock', 'number_of_items_saled')

    # def image_tag(self, obj):
    #     if obj.image:
    #         return format_html('<img src="{}" style="width: 50px; height:58px;"" />'.format(obj.image.url))

    # def image_tag(self, obj):
    #     if obj.image:
    #         return format_html('<img src="{}" style="width: 50px; height:58px;"" />'.format(obj.image.url))

    # image_tag.short_description = 'Image'


# class OrderItemsInline(admin.TabularInline):
#     model = OrderItems
#     extra = 0


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     inlines = [OrderItemsInline]
#     list_display = ('unique_code', 'customer_name', 'total_amount')
#     search_fields = ['unique_code']

# actions = ["download_invoice"]

# def download_invoice(self, request, queryset):
#     for query in queryset:
#         html_string = render_to_string('inventory/company_invoice.html', {'queryset': query})
#
#         html = HTML(string=html_string)
#         html.write_pdf(target='/tmp/mypdf.pdf')
#
#         fs = FileSystemStorage('/tmp')
#         with fs.open('mypdf.pdf') as pdf:
#             response = HttpResponse(pdf, content_type='application/pdf')
#             response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'
#             return response


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('owner_share', 'expense_share')


@admin.register(CashOrder)
class CashOrderAdmin(admin.ModelAdmin):
    list_display = ('unique_id', 'customer_name', 'sale_price', 'sale_by', 'profit', 'product')


@admin.register(SellerProfile)
class SettingProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'profit')


@admin.register(ReturnCashOrder)
class ReturnCashOrderAdmin(admin.ModelAdmin):
    list_display = ['cash_order', 'reason', 'return_amount']


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ['owner_name', 'owner_balance', 'business_balance']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['order', 'seller', 'total_profit', 'seller_profit', 'owner_profit', 'business_profit']


admin.site.register(IMEINumber)
