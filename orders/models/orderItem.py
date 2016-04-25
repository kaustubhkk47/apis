from django.db import models

from catalog.models.product import *
from .order import *
from .subOrder import *
from .orderShipment import *
from payments.models.buyerPayment import BuyerPayment
from payments.models.sellerPayment import SellerPayment

from catalog.models.product import Product

class OrderItem(models.Model):

    suborder = models.ForeignKey(SubOrder)
    product = models.ForeignKey(Product)
    order_shipment = models.ForeignKey(OrderShipment,null=True,blank=True)
    #buyerPayment = models.ForeignKey(BuyerPayment)
    seller_payment = models.ForeignKey(SellerPayment,null=True,blank=True)

    lots = models.PositiveIntegerField()
    undiscounted_price_per_piece = models.DecimalField(max_digits=10, decimal_places=2)
    actual_price_per_piece = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    cod_charge = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    lot_size = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    current_status = models.IntegerField(default=0)

    cancellation_remarks = models.TextField(blank=True)
    cancellation_time = models.DateTimeField(null=True, blank=True)

    merchant_notified_time = models.DateTimeField(null=True, blank=True)
    sent_for_pickup_time = models.DateTimeField(null=True, blank=True)
    lost_time = models.DateTimeField(null=True, blank=True)
    completed_time = models.DateTimeField(null=True, blank=True)
    closed_time = models.DateTimeField(null=True, blank=True)


    def __unicode__(self):
        return str(self.suborder.order.id) + "-" + str(self.suborder.id) + "-" + str(self.id)

def validateOrderProductsData(orderProducts):

    flag = True

    for orderProduct in orderProducts:
        if not "productID" in orderProduct or not orderProduct["productID"]!=None:
            flag = False

        productPtr = Product.objects.filter(id=orderProduct["productID"])
        if len(productPtr) == 0:
            flag = False
        if not "lots" in orderProduct or not orderProduct["lots"]!=None:
            flag = False
        if not "lot_size" in orderProduct or not orderProduct["lot_size"]!=None:
            flag = False
        if not "undiscounted_price_per_piece" in orderProduct or not orderProduct["undiscounted_price_per_piece"]!=None:
            flag = False
        if not "total_price" in orderProduct or not orderProduct["total_price"]!=None:
            flag = False
        if not "cod_charge" in orderProduct or not orderProduct["cod_charge"]!=None:
            flag = False
        if not "shipping_charge" in orderProduct or not orderProduct["shipping_charge"]!=None:
            flag = False
        if not "final_price" in orderProduct or not orderProduct["final_price"]!=None:
            flag = False
        if not "actual_price_per_piece" in orderProduct or not orderProduct["actual_price_per_piece"]!=None:
            flag = False

    return flag

def validateOrderItemStatus(status, current_status):
    if current_status == 0 and not (status == 1 or status == 10):
        return False
    elif current_status == 1 and not (status == 2 or status == 10):
        return False
    elif current_status == 2 and not(status == 3 or status == 10):
        return False
    elif current_status == 3 and not(status == 4 or status == 10):
        return False
    elif current_status == 4 and not(status == 5 or status == 6 or status == 7 or status == 9):
        return False
    elif current_status == 5 and not(status == 6 or status == 7 or status == 9):
        return False
    elif current_status == 6 and not(status == 11 or status == 7):
        return False
    elif current_status == 7 and not(status == 8 or status == 9):
        return False
    elif current_status == 8 and not(status == 12):
        return False
    elif current_status == 9 and not(status == 12):
        return False
    elif current_status == 10 and not(status == 12):
        return False
    elif current_status == 11 and not(status == 12):
        return False
    elif current_status == 12:
        return False
    return True


OrderItemStatus = {
	0:"Order Placed",
	1:"Merchant notified",
    2:"3PL notified",
    3:"3PL manifested",
    4:"3PL in transit",
    5:"3PL stuck in transit",
    6:"Delivered",
    7:"RTO in transit",
    8:"RTO delivered",
    9:"Lost",
    10:"Cancelled",
    11:"Completed",
    12:"Order Closed"
}