from __future__ import unicode_literals

from django.db import models

from users.models import Seller

class Category(models.Model):
    name = models.CharField(max_length=50, blank=False)
    display_name = models.CharField(max_length=50, blank=False)
    slug = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.display_name

class Product(models.Model):
    seller = models.ForeignKey(Seller)
    category = models.ForeignKey(Category)

    name = models.CharField(max_length=255, blank=False)

    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    unit = models.CharField(max_length=15, blank=False)
    tax = models.DecimalField(max_digits=5, decimal_places=2)

    lot_size = models.PositiveIntegerField(default=1)
    price_per_lot = models.DecimalField(max_digits=10, decimal_places=2, blank=False)

    seller_catalog_number = models.CharField(max_length=200, blank=True)
    brand = models.CharField(max_length=100, blank=True)

    slug = models.CharField(max_length=100, blank=True)
    manufactured_country = models.CharField(max_length=50, blank=True, default="India")
    warranty = models.CharField(max_length=100, blank=True)

    remarks = models.TextField()
    images = models.CommaSeparatedIntegerField(max_length=255, blank=True)
    
    verification = models.BooleanField(default=False)
    show_online = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

class ProductLot(models.Model):
    product = models.ForeignKey(Product)

    lot_size_from = models.IntegerField()
    lot_size_to = models.IntegerField()

    lot_discount = models.DecimalField(max_digits=5, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return ""
