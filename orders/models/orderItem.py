from django.db import models

from catalog.models.product import *
from catalog.models.productLot import *
from .order import *
from .subOrder import *
from .orderShipment import *
from .payments import BuyerPayment
from .payments import SellerPayment

from catalog.models.product import Product

class OrderItem(models.Model):

    suborder = models.ForeignKey(SubOrder)
    product = models.ForeignKey(Product)
    order_shipment = models.ForeignKey(OrderShipment,null=True,blank=True)
    seller_payment = models.ForeignKey(SellerPayment,null=True,blank=True)

    pieces = models.PositiveIntegerField(default=0)
    lots = models.PositiveIntegerField(default=0)
    retail_price_per_piece = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    calculated_price_per_piece = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    edited_price_per_piece = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    lot_size = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    current_status = models.IntegerField(default=0)

    remarks = models.TextField(blank=True)

    cancellation_remarks = models.TextField(blank=True)
    cancellation_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-id"]

    def __unicode__(self):
        return str(self.suborder.order.id) + "-" + str(self.suborder.id) + "-" + str(self.id)

def validateOrderProductsData(orderProducts):

    flag = True

    for orderProduct in orderProducts:
        if not "productID" in orderProduct or not orderProduct["productID"]!=None:
            flag = False

        productPtr = Product.objects.filter(id=int(orderProduct["productID"]))
        if len(productPtr) == 0:
            return False

        productPtr = productPtr[0]

        if not "pieces" in orderProduct or not orderProduct["pieces"]!=None:
            flag = False
        if not "edited_price_per_piece" in orderProduct or not orderProduct["edited_price_per_piece"]!=None:
            flag = False
        if not "remarks" in orderProduct or not orderProduct["remarks"]!=None:
            orderProduct["remarks"] = ""

        orderProduct["retail_price_per_piece"] = productPtr.price_per_unit
        orderProduct["lot_size"] = productPtr.lot_size

        if flag == True:
            orderProduct["final_price"] = Decimal(orderProduct["pieces"])*Decimal(orderProduct["edited_price_per_piece"])
            orderProduct["lots"] = int(math.ceil(float(orderProduct["pieces"])/productPtr.lot_size))
            orderProduct["calculated_price_per_piece"] = getCalculatedPricePerPiece(int(orderProduct["productID"]),orderProduct["lots"])

    return flag

def populateOrderItemData(OrderItemPtr, orderItem):
    OrderItemPtr.pieces = int(orderItem["pieces"])
    OrderItemPtr.lots = orderItem["lots"]
    OrderItemPtr.retail_price_per_piece = Decimal(orderItem["retail_price_per_piece"])
    OrderItemPtr.calculated_price_per_piece = Decimal(orderItem["calculated_price_per_piece"])
    OrderItemPtr.edited_price_per_piece = Decimal(orderItem["edited_price_per_piece"])
    OrderItemPtr.final_price = Decimal(orderItem["final_price"])
    OrderItemPtr.lot_size = int(orderItem["lot_size"])
    OrderItemPtr.remarks = orderItem["remarks"]
    OrderItemPtr.current_status = 0

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