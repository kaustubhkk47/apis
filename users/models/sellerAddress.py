from django.db import models

from .seller import Seller

class SellerAddress(models.Model):
    seller = models.ForeignKey(Seller)

    address = models.CharField(max_length=255, blank=True, null=False)
    landmark = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True, default="India")
    contact_number = models.CharField(max_length=11, blank=True)

    def __unicode__(self):
        return ""
