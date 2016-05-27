from django.db import models

from users.models.seller import *
from .order import *

class SubOrder(models.Model):

    order = models.ForeignKey(Order)
    seller = models.ForeignKey(Seller)

    product_count = models.PositiveIntegerField(default=1)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    calculated_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    edited_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    cod_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)

    suborder_status = models.IntegerField(default=0)

    display_number = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    merchant_notified_time = models.DateTimeField(null=True, blank=True)
    completed_time = models.DateTimeField(null=True, blank=True)
    closed_time = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return str(self.order.id) + "-" + str(self.id)

def populateSubOrderData(subOrderPtr, subOrder,orderID):
    
    subOrderPtr.product_count = subOrder["product_count"]
    subOrderPtr.retail_price = subOrder["retail_price"]
    subOrderPtr.calculated_price = subOrder["calculated_price"]
    subOrderPtr.edited_price = subOrder["edited_price"]
    subOrderPtr.final_price = subOrder["edited_price"]
    subOrderPtr.save()
    subOrderPtr.display_number = "1" + "%05d" %(subOrder["seller"].id,) +"%06d" %(subOrderPtr.id,) + "%06d" %(orderID,)

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
