from django.db import models

from catalog.models.product import *
from .order import *

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
