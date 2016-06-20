from django.db import models

from users.models.buyer import BuyerAddress
from users.models.seller import SellerAddress

from .orderItem import OrderItem
#from .subOrder import SubOrder

from scripts.utils import validate_date
from decimal import Decimal
import datetime

from logistics.models.logisticspartner import LogisticsPartner


class OrderShipment(models.Model):

    suborder = models.ForeignKey('orders.SubOrder')

    pickup_address = models.ForeignKey(SellerAddress)
    drop_address = models.ForeignKey(BuyerAddress)

    invoice_number = models.CharField(max_length=50, blank=True)
    invoice_date = models.DateTimeField(blank=True, null=True)

    logistics_partner = models.ForeignKey(LogisticsPartner, blank=True, null =True)
    logistics_partner_name = models.CharField(max_length=50, blank=True,null=True)
    waybill_number = models.CharField(max_length=50, blank=True,null=True)

    packaged_weight = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    packaged_length = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    packaged_breadth = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    packaged_height = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)

    cod_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)

    remarks = models.TextField(blank=True)

    current_status = models.IntegerField(default=0)

    tpl_notified_time = models.DateTimeField(null=True, blank=True)
    tpl_manifested_time = models.DateTimeField(null=True, blank=True)
    tpl_in_transit_time = models.DateTimeField(null=True, blank=True)
    tpl_stuck_in_transit_time = models.DateTimeField(null=True, blank=True)
    delivered_time = models.DateTimeField(null=True, blank=True)
    rto_in_transit_time = models.DateTimeField(null=True, blank=True)
    rto_delivered_time = models.DateTimeField(null=True, blank=True)
    sent_for_pickup_time = models.DateTimeField(null=True, blank=True)
    lost_time = models.DateTimeField(null=True, blank=True)

    tracking_url = models.URLField(null=True, blank=True)

    rto_remarks = models.TextField(blank=True,null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    manifest_link = models.TextField(blank=True)

    class Meta:
        ordering = ["-id"]

    def __unicode__(self):
        return str(self.id) + " - " + self.suborder.display_number + " - " + self.suborder.seller.name

def validateOrderShipmentData(orderShipment):

    flag = True

    if not "invoice_number" in orderShipment or orderShipment["invoice_number"]==None:
        orderShipment["invoice_number"] = ""
    if not "invoice_date" in orderShipment or orderShipment["invoice_date"]==None or not validate_date(orderShipment["invoice_date"]):
        flag = False
    if not "waybill_number" in orderShipment or orderShipment["waybill_number"]==None:
        orderShipment["waybill_number"] = ""
    if not "packaged_weight" in orderShipment or orderShipment["packaged_weight"]==None:
        flag = False
    if not "packaged_length" in orderShipment or orderShipment["packaged_length"]==None:
        flag = False
    if not "packaged_breadth" in orderShipment or orderShipment["packaged_breadth"]==None:
        flag = False
    if not "packaged_height" in orderShipment or orderShipment["packaged_height"]==None:
        flag = False
    if not "cod_charge" in orderShipment or orderShipment["cod_charge"]==None:
        flag = False
    if not "shipping_charge" in orderShipment or orderShipment["shipping_charge"]==None:
        flag = False
    if not "remarks" in orderShipment or orderShipment["remarks"]==None:
        orderShipment["remarks"] = ""
    if not "rto_remarks" in orderShipment or orderShipment["rto_remarks"]==None:
        orderShipment["rto_remarks"] = ""
    if not "tracking_url" in orderShipment or orderShipment["tracking_url"]==None:
        orderShipment["tracking_url"] = ""
    if not "all_items" in orderShipment or orderShipment["all_items"]==None:
        flag = False
    
    return flag

def populateOrderShipment(OrderShipmentPtr, orderShipment):
    OrderShipmentPtr.invoice_number = orderShipment["invoice_number"]
    OrderShipmentPtr.invoice_date = orderShipment["invoice_date"]
    OrderShipmentPtr.logistics_partner_name = "Fedex"
    logistics_partner = LogisticsPartner.objects.get(id=1)
    OrderShipmentPtr.logistics_partner = logistics_partner
    OrderShipmentPtr.waybill_number = orderShipment["waybill_number"]
    OrderShipmentPtr.packaged_weight = Decimal(orderShipment["packaged_weight"])
    OrderShipmentPtr.packaged_length = Decimal(orderShipment["packaged_length"])
    OrderShipmentPtr.packaged_breadth = Decimal(orderShipment["packaged_breadth"])
    OrderShipmentPtr.packaged_height = Decimal(orderShipment["packaged_height"])
    OrderShipmentPtr.cod_charge = Decimal(orderShipment["cod_charge"])
    OrderShipmentPtr.shipping_charge = Decimal(orderShipment["shipping_charge"])
    OrderShipmentPtr.remarks = orderShipment["remarks"]
    OrderShipmentPtr.rto_remarks = orderShipment["rto_remarks"]
    OrderShipmentPtr.tracking_url = "https://www.fedex.com/apps/fedextrack/?action=track&trackingnumber="+orderShipment["waybill_number"]+"&cntry_code=in"
    OrderShipmentPtr.current_status = 3
    OrderShipmentPtr.tpl_manifested_time = datetime.datetime.now()

def filterOrderShipment(orderShipmentParameters):
    orderShipments = OrderShipment.objects.all().select_related('suborder','pickup_address','drop_address')
        
    if "orderShipmentArr" in orderShipmentParameters:
        orderShipments = orderShipments.filter(id__in=orderShipmentParameters["orderShipmentArr"])

    if "orderShipmentStatusArr" in orderShipmentParameters:
        orderShipments = orderShipments.filter(current_status__in=orderShipmentParameters["orderShipmentStatusArr"])

    if "subOrderArr" in orderShipmentParameters:
        orderShipments = orderShipments.filter(suborder_id__in=orderShipmentParameters["subOrderArr"])

    if "sellersArr" in orderShipmentParameters:
        orderShipments = orderShipments.filter(suborder__seller_id__in=orderShipmentParameters["sellersArr"])

    return orderShipments

def validateOrderShipmentItemsData(orderItems, subOrderID):

    for orderItem in orderItems:

        if not "orderitemID" in orderItem or orderItem["orderitemID"]==None:
            return False

        orderItemPtr = OrderItem.objects.filter(id=int(orderItem["orderitemID"]))
        if len(orderItemPtr) == 0:
            return False

        orderItemPtr = orderItemPtr[0]

        if orderItemPtr.current_status >= 4:
            return False

        if orderItemPtr.order_shipment != None:
            return False

        if orderItemPtr.suborder_id != subOrderID:
            return False

    return True

OrderShipmentStatus = {
    0:{"display_value":"Sent for Pickup","display_time":"sent_for_pickup_time"},
    1:{"display_value":"Shipment created","display_time":"created_at"},
    2:{"display_value":"3PL notified","display_time":"tpl_notified_time"},
    3:{"display_value":"3PL manifested","display_time":"tpl_manifested_time"},
    4:{"display_value":"3PL in transit","display_time":"tpl_in_transit_time"},
    5:{"display_value":"3PL stuck in transit","display_time":"tpl_stuck_in_transit_time"},
    6:{"display_value":"Delivered","display_time":"delivered_time"},
    7:{"display_value":"RTO in transit","display_time":"rto_in_transit_time"},
    8:{"display_value":"RTO delivered","display_time":"rto_delivered_time"},
    9:{"display_value":"Lost","display_time":"lost_time"}
}

def validateOrderShipmentStatus(status, current_status):

    if status not in [4,5,6,7,8,9]:
        return False

    if current_status == 3 and not(status == 4):
        return False
    if current_status == 4 and not(status == 5 or status == 6 or status == 7 or status == 9):
        return False
    elif current_status == 5 and not(status == 4 or status == 6 or status == 7 or status == 9):
        return False
    elif current_status == 6:
        return False
    elif current_status == 7 and not(status == 4 or status == 8 or status == 9):
        return False
    elif current_status == 8:
        return False
    elif current_status == 9:
        return False
    return True

