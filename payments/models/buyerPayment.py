from django.db import models

from users.models.buyer import *
from users.models.internalUser import *

class BuyerPayment(models.Model):
    buyer = models.ForeignKey(Buyer)
    internal_user = models.ForeignKey(InternalUser)

    payment_method = models.CharField(max_length=50, blank=False)
    reference_number = models.CharField(max_length=255, blank=True)
    payment_date = models.DateTimeField(blank=True, null=True)

    details = models.TextField(blank=True)

    def __unicode__(self):
        return self.reference_number
