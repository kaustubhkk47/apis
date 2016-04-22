from django.db import models

from users.models.buyer import *
from users.models.seller import *

class Order(models.Model):
    buyer = models.ForeignKey(Buyer)
    seller = models.ForeignKey(Seller)

    product_count = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(max_length=50, blank=True, null=False)
    order_status = models.BooleanField(default=False)
    shipping_status = models.CharField(max_length=50, blank=True)

    remarks = models.TextField(blank=True)

    order_confirmation = models.BooleanField(default=False)

    delivered_at = models.DateTimeField(null=True)

    rto_delivered_at = models.DateTimeField(null=True)
    rto_remarks = models.TextField(blank=True)

    cancellation_remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return ""
"""
orderStatus = {
    "unconfirmed" : {
        value:0,
        display_value:"Pending confirmation"
    },
    "confirmed" : {
        value:1
    },
    "seller_notified" :{
        value:2,
    },
    ""

    }
"""