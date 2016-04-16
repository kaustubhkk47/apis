from django.db import models

from users.models.buyer import *

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
