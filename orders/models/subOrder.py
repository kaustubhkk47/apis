from django.db import models

from users.models.seller import Seller
#from orders.models.order import Order
from orders.models.orderItem import OrderItem, OrderItemCompletionStatus

import datetime
from decimal import Decimal

class SubOrder(models.Model):

    order = models.ForeignKey('orders.Order')
    seller = models.ForeignKey(Seller)

    product_count = models.PositiveIntegerField(default=1)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    calculated_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    edited_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    cod_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)

    suborder_status = models.IntegerField(default=0)
    suborder_payment_status = models.IntegerField(default=0)

    display_number = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    confirmed_time = models.DateTimeField(null=True, blank=True)
    merchant_notified_time = models.DateTimeField(null=True, blank=True)
    completed_time = models.DateTimeField(null=True, blank=True)
    closed_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-id"]

    def __unicode__(self):
        return str(self.id) + " - " + str(self.display_number) + " - " + self.seller.name + " - Price: " + str(self.final_price)

def populateSubOrderData(subOrderPtr, subOrder,orderID):
    
    subOrderPtr.product_count = int(subOrder["product_count"])
    subOrderPtr.retail_price = Decimal(subOrder["retail_price"])
    subOrderPtr.calculated_price = Decimal(subOrder["calculated_price"])
    subOrderPtr.edited_price = Decimal(subOrder["edited_price"])
    subOrderPtr.final_price = subOrder["edited_price"]
    subOrderPtr.suborder_status = 1
    subOrderPtr.confirmed_time = datetime.datetime.now()
    subOrderPtr.save()
    subOrderPtr.display_number = "%04d" %(subOrder["seller"].id,) + "-" + "1" + "%06d" %(orderID,)

def validateSubOrderStatus(status, current_status):

    if status not in [2]:
        return False

    if current_status == 0:
        return False
    elif current_status == 1 and not(status == 2):
        return False
    elif current_status == 2:
        return False
    elif current_status == 3:
        return False
    elif current_status == 4:
        return False

    return True

def filterSubOrder(subOrderParameters):
    subOrders = SubOrder.objects.all().select_related('seller','order__buyer')
        
    if "subOrderArr" in subOrderParameters:
        subOrders = subOrders.filter(id__in=subOrderParameters["subOrderArr"])

    if "subOrderStatusArr" in subOrderParameters:
        subOrders = subOrders.filter(suborder_status__in=subOrderParameters["subOrderStatusArr"])

    if "subOrderPaymentStatusArr" in subOrderParameters:
        subOrders = subOrders.filter(suborder_payment_status__in=subOrderParameters["subOrderPaymentStatusArr"])

    if "sellersArr" in subOrderParameters:
        subOrders = subOrders.filter(seller_id__in=subOrderParameters["sellersArr"])

    if "orderArr" in subOrderParameters:
        subOrders = subOrders.filter(order_id__in=subOrderParameters["orderArr"])

    return subOrders

def update_suborder_completion_status(subOrder):

    orderItemQuerySet = OrderItem.objects.filter(suborder_id = subOrder.id)
    for orderItem in orderItemQuerySet:
        if orderItem.current_status not in OrderItemCompletionStatus:
            return

    subOrder.suborder_status = 4
    subOrder.save()

SubOrderStatus = {
    -1:{"display_value":"Cancelled"},
    0:{"display_value":"Unconfirmed"},
    1:{"display_value":"Confirmed"},
    2:{"display_value":"Merchant Notified"},
    3:{"display_value":"Partially Shipped"},
    4:{"display_value":"Shipped"},
    5:{"display_value":"Completed"}
}

SubOrderPaymentStatus = {
    0:{"display_value":"Not Paid"},
    1:{"display_value":"Paid"},
    2:{"display_value":"Partially paid"}
}