from django.db import models

from users.models.buyer import *
#from users.models.seller import *

class Order(models.Model):

    buyer = models.ForeignKey(Buyer)

    product_count = models.PositiveIntegerField(default=1)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    calculated_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    edited_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    cod_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    
    order_status = models.IntegerField(default=0)

    display_number = models.CharField(max_length=20, blank=True)

    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.id)

def populateOrderData(orderPtr, order):
    orderPtr.product_count = order["product_count"]
    orderPtr.retail_price = order["retail_price"]
    orderPtr.calculated_price = order["calculated_price"]
    orderPtr.edited_price = order["edited_price"]
    orderPtr.final_price = order["edited_price"]
    orderPtr.remarks = order["remarks"]
    orderPtr.order_status = 1
    orderPtr.save()
    orderPtr.display_number = "1" +"%06d" %(orderPtr.id,)

orderStatus = {
    0:"Placed",
    1:"Confirmed",
    2:"Completed"
}

