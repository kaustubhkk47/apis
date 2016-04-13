from __future__ import unicode_literals

from django.db import models

from users.models import *
from catalog.models import Product

class Order(models.Model):
    buyer = models.ForeignKey(Buyer)

    product_count = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(max_length=50, blank=True, null=False)
    order_status = models.BooleanField(default=False)
    shipping_status = models.CharField(max_length=50, blank=True)

    order_confirmation = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return ""

class OrderItem(models.Model):
    order = models.ForeignKey(Order)
    product = models.ForeignKey(Product)

    lots = models.PositiveIntegerField()
    price_per_lot = models.PositiveIntegerField()

    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return ""

class OrderShipment(models.Model):
    order = models.ForeignKey(Order)
    seller = models.ForeignKey(Seller)
    buyer = models.ForeignKey(Buyer)

    pickup = models.ForeignKey(SellerAddress)
    drop = models.ForeignKey(BuyerAddress)

    invoice_number = models.CharField(max_length=50, blank=True)
    invoice_date = models.DateTimeField(blank=True, null=True)

    logistics_partner = models.CharField(max_length=50, blank=True)

    packaged_weight = models.DecimalField(max_digits=10, decimal_places=2)
    packaged_length = models.DecimalField(max_digits=10, decimal_places=2)
    packaged_breadth = models.DecimalField(max_digits=10, decimal_places=2)
    packaged_height = models.DecimalField(max_digits=10, decimal_places=2)

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return ""
