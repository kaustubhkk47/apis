from django.db import models

from users.models.seller import *
from .order import *

class SubOrder(models.Model):

    order = models.ForeignKey(Order)

    seller = models.ForeignKey(Seller)
    product_count = models.PositiveIntegerField(default=1)
    undiscounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #payment_status = models.PositiveIntegerField(default=0)
    #suborder_status = models.PositiveIntegerField(default=0)
    #shipping_status = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return str(self.order.id) + "-" + str(self.id)

subOrderPaymentStatus = {
    "not_paid_to_seller": {
        "value": 0,
        "display_value": "Not paid to seller"
    },
    "paid_to_seller": {
        "value": 1,
        "display_value": "Paid to seller"
    }
}

subOrderStatus = {
    "unconfirmed": {
        "value": 0,
        "display_value": "Pending confirmation"
    },
    "confirmed": {
        "value": 1,
        "display_value": "Confirmed by seller"
    },
}
