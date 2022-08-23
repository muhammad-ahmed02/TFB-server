from django.contrib import admin

from .models import *


@admin.register(ProductStockIn)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'purchasing_price', 'available_stock', 'sold', 'on_credit', 'on_claim', 'asset')

    search_fields = ('product__name', 'purchasing_price', 'available_stock', 'sold', 'on_credit', 'on_claim')

    # def image_tag(self, obj):
    #     if obj.image:
    #         return format_html('<img src="{}" style="width: 50px; height:58px;"" />'.format(obj.image.url))

    # def image_tag(self, obj):
    #     if obj.image:
    #         return format_html('<img src="{}" style="width: 50px; height:58px;"" />'.format(obj.image.url))

    # image_tag.short_description = 'Image'


class CashOrderItemsInline(admin.TabularInline):
    model = CashOrderItem
    extra = 0


class CreditItemInline(admin.TabularInline):
    model = CreditItem
    extra = 0


@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    inlines = [CreditItemInline]
    list_display = ['payment_status', 'quantity']


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['product', 'vendor', 'imei_or_serial_number', 'reason']


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('owner_share', 'expense_share')


@admin.register(CashOrder)
class CashOrderAdmin(admin.ModelAdmin):
    inlines = [CashOrderItemsInline]
    list_display = ('unique_id', 'customer_name', 'sale_by', 'total_amount', 'total_profit')


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'profit', 'seller_share', 'business_share')


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
admin.site.register(Product)
admin.site.register(Vendor)
# admin.site.register(CashOrderItem)
# admin.site.register(CreditItem)
