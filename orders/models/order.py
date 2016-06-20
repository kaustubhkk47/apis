from django.db import models

from users.models.buyer import Buyer
from catalog.models.product import Product
from catalog.models.productLot import getCalculatedPricePerPiece
from .orderItem import OrderItem, OrderItemCompletionStatus

from decimal import Decimal
import math

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
    order_payment_status = models.IntegerField(default=0)

    display_number = models.CharField(max_length=20, blank=True)

    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __unicode__(self):
        return str(self.id) + " - " + str(self.display_number) + " - " + self.buyer.name + " - Price: " + str(self.final_price)

def populateOrderData(orderPtr, order):
    orderPtr.product_count = order["product_count"]
    orderPtr.retail_price = order["retail_price"]
    orderPtr.calculated_price = order["calculated_price"]
    orderPtr.edited_price = order["edited_price"]
    orderPtr.final_price = round(order["edited_price"])
    orderPtr.remarks = order["remarks"]
    orderPtr.order_status = 1
    orderPtr.save()
    orderPtr.display_number = "1" +"%06d" %(orderPtr.id,)

def filterOrder(orderParameters):
    orders = Order.objects.all().select_related('buyer')
        
    if "orderArr" in orderParameters:
        orders = orders.filter(id__in=orderParameters["orderArr"])

    if "orderStatusArr" in orderParameters:
        orders = orders.filter(order_status__in=orderParameters["orderStatusArr"])

    if "orderPaymentStatusArr" in orderParameters:
        orders = orders.filter(order_payment_status__in=orderParameters["orderPaymentStatusArr"])

    if "buyersArr" in orderParameters:
        orders = orders.filter(buyer_id__in=orderParameters["buyersArr"])

    return orders

def validateOrderProductsData(orderProducts):

    flag = True

    for orderProduct in orderProducts:
        if not "productID" in orderProduct or orderProduct["productID"]==None:
            flag = False

        productPtr = Product.objects.filter(id=int(orderProduct["productID"]))
        if len(productPtr) == 0:
            return False

        productPtr = productPtr[0]

        if not "pieces" in orderProduct or orderProduct["pieces"]==None:
            flag = False
        if not "edited_price_per_piece" in orderProduct or orderProduct["edited_price_per_piece"]==None:
            flag = False
        if not "remarks" in orderProduct or orderProduct["remarks"]==None:
            orderProduct["remarks"] = ""

        orderProduct["retail_price_per_piece"] = productPtr.price_per_unit
        orderProduct["lot_size"] = productPtr.lot_size

        if flag == True:
            orderProduct["final_price"] = Decimal(orderProduct["pieces"])*Decimal(orderProduct["edited_price_per_piece"])
            orderProduct["lots"] = int(math.ceil(float(orderProduct["pieces"])/productPtr.lot_size))
            orderProduct["calculated_price_per_piece"] = getCalculatedPricePerPiece(int(orderProduct["productID"]),orderProduct["lots"])

    return flag

def update_order_completion_status(order):

    orderItemQuerySet = OrderItem.objects.filter(suborder__order_id = order.id)
    for orderItem in orderItemQuerySet:
        if orderItem.current_status not in OrderItemCompletionStatus:
            return

    order.order_status = 3
    order.save()

OrderStatus = {
    0:{"display_value":"Placed"},
    1:{"display_value":"Confirmed"},
    2:{"display_value":"Partially Shipped"},
    3:{"display_value":"Shipped"},
    4:{"display_value":"Completed"}
}

OrderPaymentStatus = {
    0:{"display_value":"Not Paid"},
    1:{"display_value":"Paid"},
    2:{"display_value":"Partially paid"}
}

## Status: Placed, confirmed, shipped, delivered
## Payment status : paid, not paid, partially paid

