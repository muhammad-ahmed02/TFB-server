from django.contrib.auth.models import User
from django.db import models
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver


class products(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    purchasing_price = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    selling_price = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    imei_or_serial_number = models.CharField(max_length=200, null=True, blank=True)
    available_stock = models.IntegerField(default=0)
    number_of_items_saled = models.IntegerField(default=0, editable=False)
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name


class Order(models.Model):
    unique_code = models.UUIDField(default=uuid.uuid4, editable=False)
    customer_name = models.CharField(max_length=200, null=True, blank=True)
    customer_phone = models.CharField(max_length=200, null=True, blank=True)
    warrenty = models.CharField(max_length=200, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True, editable=False)
    
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return str(self.unique_code)
    
        
class OrderItems(models.Model):
    product = models.ForeignKey(products, on_delete=models.CASCADE,null=True,blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.IntegerField(default=1,null=True,blank=True)

    def calculate_total_amount(self):
        order_items = OrderItems.objects.filter(order__id = self.order.id)
        ammount = 0
        for items in order_items:
            ammount += items.product.selling_price * items.quantity
        order = Order.objects.get(id = self.order.id)
        order.total_ammunt = ammount
        order.save()
    
    def save(self, *args, **kwargs):
        super(OrderItems, self).save(*args, **kwargs)
        self.calculate_total_amount()

@receiver(post_save, sender=OrderItems, dispatch_uid="update_stock_count")
def update_stock(sender, instance, **kwargs):
    quantity = instance.quantity
    product = products.objects.get(id = instance.product.id)
    product.available_stock -= quantity
    product.number_of_items_saled += quantity
    product.save()
