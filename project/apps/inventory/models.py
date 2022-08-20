import string
import random
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


def generate_join_code(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class IMEINumber(models.Model):
    number = models.CharField(max_length=200, unique=True, primary_key=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.number


class Vendor(models.Model):
    name = models.CharField(max_length=64)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name


class ProductStockIn(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    purchasing_price = models.IntegerField()
    imei_or_serial_number = models.ManyToManyField(IMEINumber, blank=True)
    available_stock = models.PositiveIntegerField(default=0)
    sold = models.PositiveIntegerField(default=0)
    on_credit = models.PositiveIntegerField(default=0)
    on_claim = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.product.name


# class Order(models.Model):
#     unique_code = models.CharField(max_length=10, default=generate_join_code, unique=True, editable=False)
#     customer_name = models.CharField(max_length=200, null=True, blank=True)
#     customer_phone = models.CharField(max_length=200, null=True, blank=True)
#     warranty = models.CharField(max_length=200, null=True, blank=True)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, editable=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     total_amount = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True, editable=False)
#
#     def __str__(self):
#         return str(self.unique_code)


# class OrderItems(models.Model):
#     product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
#     quantity = models.IntegerField(default=1, null=True, blank=True)
#     selling_price = models.DecimalField(decimal_places=2, max_digits=20)
#     imei = models.CharField(max_length=200, null=True, blank=True)
#
#     def calculate_total_amount(self):
#         order_items = OrderItems.objects.filter(order__id=self.order.id)
#         amount = 0
#         for items in order_items:
#             amount += items.selling_price * items.quantity
#         order = Order.objects.get(id=self.order.id)
#         order.total_amount = amount
#         order.save()
#
#     def save(self, *args, **kwargs):
#         super(OrderItems, self).save(*args, **kwargs)
#         self.calculate_total_amount()


class SellerProfile(models.Model):
    username = models.CharField(max_length=54)
    profit = models.IntegerField(default=0)
    business_share = models.PositiveIntegerField()
    seller_share = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.username


class CompanyProfile(models.Model):
    owner_name = models.CharField(max_length=54)
    owner_balance = models.IntegerField(default=0)
    business_balance = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.owner_name


class Setting(models.Model):
    status_choices = (
        ('UP', 'up'),
        ('DOWN', 'down'),
    )

    owner_share = models.PositiveIntegerField()
    expense_share = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=status_choices, default="UP")

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


class CashOrder(models.Model):
    unique_id = models.CharField(max_length=10, default=generate_join_code, unique=True)
    customer_name = models.CharField(max_length=54, null=True, blank=True)
    product_stock = models.ForeignKey(ProductStockIn, on_delete=models.CASCADE)
    sale_by = models.ForeignKey(SellerProfile, on_delete=models.CASCADE)
    sale_price = models.IntegerField()
    profit_per_device = models.IntegerField(null=True, blank=True)
    total_profit = models.IntegerField(null=True, blank=True)
    warranty = models.PositiveIntegerField(default=0, help_text="in days")
    imei_or_serial_number = models.ManyToManyField(IMEINumber)
    quantity = models.IntegerField(default=1)
    total_amount = models.IntegerField(null=True, blank=True, help_text="Calculated Automatically")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.unique_id

    def save(self, *args, **kwargs):
        self.profit_per_device = self.sale_price - self.product_stock.purchasing_price
        self.total_profit = self.profit_per_device * self.quantity
        self.total_amount = self.sale_price * self.quantity
        super(CashOrder, self).save(*args, **kwargs)


@receiver(post_save, sender=CashOrder, dispatch_uid="update_stock_count")
def update_stock(sender, instance, **kwargs):
    quantity = instance.quantity
    product_stock_in = ProductStockIn.objects.get(id=instance.product_stock.id)
    product_stock_in.available_stock -= quantity
    product_stock_in.sold += quantity
    product_stock_in.save()


class ReturnCashOrder(models.Model):
    return_reasons = (
        ('NOT_INTERESTED', 'Not Interested'),
        ('ISSUE', 'Issue'),
        ('CUSTOM', 'Custom'),
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
            self.return_amount = self.cash_order.product_stock.purchasing_price * self.cash_order.quantity
        elif self.reason == "ISSUE":
            self.return_amount = self.cash_order.sale_price

            seller = SellerProfile.objects.get(id=self.cash_order.sale_by.id)
            seller_share = Setting.objects.all()[0].seller_share
            # seller share calculated from profit
            seller_profit = ((self.cash_order.profit * seller_share) / 100)
            seller.profit -= seller_profit
            seller.save()
        else:
            # calculate profit
            sale_price = self.cash_order.sale_price
            profit = sale_price - self.return_amount

            seller = SellerProfile.objects.get(id=self.cash_order.sale_by.id)
            seller_share = Setting.objects.all()[0].seller_share

            # profit added
            seller_profit = ((profit * seller_share) / 100)
            seller.profit += seller_profit

            # previous profit deducted
            seller_prev_profit = ((self.cash_order.profit * seller_share) / 100)
            seller.profit -= seller_prev_profit

            seller.save()

        super(ReturnCashOrder, self).save(*args, **kwargs)


class Transaction(models.Model):
    order = models.ForeignKey(CashOrder, on_delete=models.CASCADE)
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    total_profit = models.IntegerField()
    seller_profit = models.IntegerField()
    owner_profit = models.IntegerField()
    business_profit = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order.unique_id

    def save(self, *args, **kwargs):
        self.total_profit = self.order.profit
        self.seller_profit = ((self.order.profit * self.seller.seller_share) / 100)

        settings = Setting.objects.filter().first()
        self.owner_profit = ((self.order.profit * settings.owner_share) / 100)
        self.business_profit = ((self.order.profit * self.seller.business_share) / 100)

        seller = SellerProfile.objects.get(id=self.seller.id)
        seller.profit += self.seller_profit
        seller.save()

        company = CompanyProfile.objects.get(id=self.company.id)
        company.owner_balance += self.owner_profit
        company.business_balance += self.business_profit
        company.save()

        super(Transaction, self).save(*args, **kwargs)
