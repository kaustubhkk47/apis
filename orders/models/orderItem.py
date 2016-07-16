from django.db import models

from catalog.models.productLot import *
#from .subOrder import SubOrder
#from .orderShipment import OrderShipment
#from .payments import SellerPayment

from catalog.models.product import Product

class OrderItem(models.Model):

    suborder = models.ForeignKey('orders.SubOrder')
    product = models.ForeignKey('catalog.Product')
    order_shipment = models.ForeignKey('orders.OrderShipment',null=True,blank=True)
    seller_payment = models.ForeignKey('orders.SellerPayment',null=True,blank=True)

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

    buyer_payment_status = models.BooleanField(default=False)

    remarks = models.TextField(blank=True)

    cancellation_remarks = models.TextField(blank=True)
    cancellation_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-id"]

    def __unicode__(self):
        return str(self.id) + " - " + self.suborder.display_number + " - Price: " + str(self.final_price) + "-" + self.product.display_name + " - " + self.product.seller.name

def populateOrderItemData(OrderItemPtr, orderItem):
    OrderItemPtr.pieces = int(orderItem["pieces"])
    OrderItemPtr.lots = int(orderItem["lots"])
    OrderItemPtr.retail_price_per_piece = Decimal(orderItem["retail_price_per_piece"])
    OrderItemPtr.calculated_price_per_piece = Decimal(orderItem["calculated_price_per_piece"])
    OrderItemPtr.edited_price_per_piece = Decimal(orderItem["edited_price_per_piece"])
    OrderItemPtr.final_price = Decimal(orderItem["final_price"])
    OrderItemPtr.lot_size = int(orderItem["lot_size"])
    OrderItemPtr.remarks = orderItem["remarks"]
    OrderItemPtr.current_status = 1

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

def update_order_item_status(orderShipmentID, status):

    orderItemQuerySet = OrderItem.objects.filter(order_shipment_id =orderShipmentID).update(current_status = status)

def filterOrderItem(orderItemParameters):
    orderItems = OrderItem.objects.all().select_related('product')
        
    if "orderItemArr" in orderItemParameters:
        orderItems = orderItems.filter(id__in=orderItemParameters["orderItemArr"])

    if "orderItemStatusArr" in orderItemParameters:
        orderItems = orderItems.filter(current_status__in=orderItemParameters["orderItemStatusArr"])

    if "sellersArr" in orderItemParameters:
        orderItems = orderItems.filter(suborder__seller_id__in=orderItemParameters["sellersArr"])

    if "subOrderArr" in orderItemParameters:
        orderItems = orderItems.filter(suborder_id__in=orderItemParameters["subOrderArr"])

    if "orderArr" in orderItemParameters:
        orderItems = orderItems.filter(suborder__order_id__in=orderItemParameters["orderArr"])

    if "orderShipmentArr" in orderItemParameters:
        orderItems = orderItems.filter(order_shipment_id__in=orderItemParameters["orderShipmentArr"])

    return orderItems


OrderItemStatus = {
	0:{"display_value":"Placed"},
    1:{"display_value":"Confirmed"},
	2:{"display_value":"Merchant notified"},
    3:{"display_value":"Shipped"},
    4:{"display_value":"Cancelled"},
    5:{"display_value":"Sent for Pickup"},
    6:{"display_value":"Shipment created"},
    7:{"display_value":"3PL notified"},
    8:{"display_value":"3PL manifested"},
    9:{"display_value":"3PL in transit"},
    10:{"display_value":"3PL stuck in transit"},
    11:{"display_value":"Delivered"},
    12:{"display_value":"RTO in transit"},
    13:{"display_value":"RTO delivered"},
    14:{"display_value":"Lost"}
}

OrderItemCompletionStatus = [4, 11, 13, 14]

def populateMailOrderItem(OrderItemPtr):

    productPtr = Product.objects.filter(id=OrderItemPtr.product_id)
    productPtr = productPtr[0]

    imageLink = "http://api.wholdus.com/" + productPtr.image_path + "200x200/" + productPtr.image_name + "-1.jpg"
    productLink = "http://www.wholdus.com/" + productPtr.category.slug + "-" + str(productPtr.category_id) + "/" +productPtr.slug +"-" + str(productPtr.id)
    itemMargin = float((OrderItemPtr.retail_price_per_piece - OrderItemPtr.edited_price_per_piece)/OrderItemPtr.retail_price_per_piece*100)

    mailOrderItem = {
        "name":productPtr.display_name,
        "catalog_number":productPtr.productdetails.seller_catalog_number,
        "pieces":OrderItemPtr.pieces,
        "price_per_piece":OrderItemPtr.edited_price_per_piece,
        "final_price":OrderItemPtr.final_price,
        "image_link":imageLink,
        "product_link":productLink,
        "margin":'{0:.1f}'.format(itemMargin)
    }
        
    if OrderItemPtr.remarks != "":
        mailOrderItem["remarks"] = OrderItemPtr.remarks

    return mailOrderItem