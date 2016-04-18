from django.db import models

from users.models.seller import *
from users.models.internalUser import *

class SellerPayment(models.Model):
    seller = models.ForeignKey(Seller)
    internal_user = models.ForeignKey(InternalUser)

    payment_method = models.CharField(max_length=50, blank=False)
    reference_number = models.CharField(max_length=255, blank=True)
    payment_date = models.DateTimeField(blank=True, null=True)

    details = models.TextField(blank=True)

    def __unicode__(self):
        return ""
