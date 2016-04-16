from django.db import models

from .product import Product

class ProductLot(models.Model):
    product = models.ForeignKey(Product)

    lot_size_from = models.IntegerField()
    lot_size_to = models.IntegerField()

    lot_discount = models.DecimalField(max_digits=5, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return ""
