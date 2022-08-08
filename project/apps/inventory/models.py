import string
import random
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


def generate_join_code(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Products(models.Model):
    name = models.CharField(max_length=200, unique=True)
    purchasing_price = models.IntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    imei_or_serial_number = models.CharField(max_length=200, null=True, blank=True)
    available_stock = models.IntegerField(default=0)
    number_of_items_saled = models.IntegerField(default=0, editable=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name


class Order(models.Model):
    unique_code = models.CharField(max_length=10, default=generate_join_code, unique=True, editable=False)
    customer_name = models.CharField(max_length=200, null=True, blank=True)
    customer_phone = models.CharField(max_length=200, null=True, blank=True)
    warranty = models.CharField(max_length=200, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True, editable=False)

    def __str__(self):
        return str(self.unique_code)


class OrderItems(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1, null=True, blank=True)
    selling_price = models.DecimalField(decimal_places=2, max_digits=20)
    imei = models.CharField(max_length=200, null=True, blank=True)

    def calculate_total_amount(self):
        order_items = OrderItems.objects.filter(order__id=self.order.id)
        amount = 0
        for items in order_items:
            amount += items.selling_price * items.quantity
        order = Order.objects.get(id=self.order.id)
        order.total_amount = amount
        order.save()

    def save(self, *args, **kwargs):
        super(OrderItems, self).save(*args, **kwargs)
        self.calculate_total_amount()


class SellerProfile(models.Model):
    username = models.CharField(max_length=54)
    profit = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.username


class Setting(models.Model):
    status_choices = (
        ('UP', 'up'),
        ('DOWN', 'down'),
    )

    seller_share = models.PositiveIntegerField()
    owner_share = models.PositiveIntegerField()
    business_share = models.PositiveIntegerField()
    expense_share = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=status_choices, default="UP")

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


class CashOrder(models.Model):
    unique_id = models.CharField(max_length=10, default=generate_join_code, unique=True)
    customer_name = models.CharField(max_length=54, null=True, blank=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    sale_by = models.ForeignKey(SellerProfile, on_delete=models.CASCADE)
    sale_price = models.IntegerField()
    profit = models.IntegerField(null=True, blank=True)
    warranty = models.PositiveIntegerField(default=0, help_text="in days")
    # quantity = models.IntegerField(default=1, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.unique_id

    def save(self, *args, **kwargs):

        self.profit = self.sale_price - self.product.purchasing_price

        seller_share = Setting.objects.all()[0].seller_share
        seller_profit = ((self.profit * seller_share) / 100)

        seller = SellerProfile.objects.get(id=self.sale_by.id)
        seller.profit = seller_profit
        seller.save()
        super(CashOrder, self).save(*args, **kwargs)

        '''
        update price logic for multiple quantity
        '''


@receiver(post_save, sender=CashOrder, dispatch_uid="update_stock_count")
def update_stock(sender, instance, **kwargs):
    # quantity = instance.quantity
    quantity = 1
    product = Products.objects.get(id=instance.product.id)
    product.available_stock -= quantity
    product.number_of_items_saled += quantity
    product.save()


class ReturnCashOrder(models.Model):
    return_reasons = (
        ('NOT_INTERESTED', 'Not Interested'),
        ('ISSUE', 'Issue'),
    )
    cash_order = models.ForeignKey(CashOrder, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=return_reasons)
    return_amount = models.IntegerField(null=True, blank=True, help_text="To be filled automatically")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cash_order.unique_id

    def save(self, *args, **kwargs):

        if self.reason == "NOT_INTERESTED":
            self.return_amount = self.cash_order.product.purchasing_price
        else:
            self.return_amount = self.cash_order.sale_price

            seller = SellerProfile.objects.get(id=self.cash_order.sale_by.id)
            seller_share = Setting.objects.all()[0].seller_share

            seller_profit = ((self.cash_order.profit * seller_share) / 100)
            seller.profit -= seller_profit
            seller.save()

        super(ReturnCashOrder, self).save(*args, **kwargs)
