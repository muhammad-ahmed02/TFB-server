from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML


@admin.register(products)
class ProductAdmin(admin.ModelAdmin):
    list_display=('name', 'purchasing_price', 'available_stock', 'number_of_items_saled')
    search_fields = ['name']

    # def image_tag(self, obj):
    #     if obj.image:
    #         return format_html('<img src="{}" style="width: 50px; height:58px;"" />'.format(obj.image.url))

    # image_tag.short_description = 'Image'

class OrderItemsInline(admin.TabularInline):
    model = OrderItems
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemsInline]
    list_display=('unique_code','customer_name','total_ammunt')
    search_fields = ['unique_code']

    actions = ["download_invoice"]

    def download_invoice(self, request, queryset):
        for query in queryset:
            html_string = render_to_string('inventory/company_invoice.html', {'queryset':query})

            html = HTML(string=html_string)
            html.write_pdf(target='/tmp/mypdf.pdf')

            fs = FileSystemStorage('/tmp')
            with fs.open('mypdf.pdf') as pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'
                return response

            return response
