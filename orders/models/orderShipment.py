from django.db import models

from users.models.buyer import *
from users.models.seller import *
from users.models.buyerAddress import *
from users.models.sellerAddress import *

from .order import *

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
