from django.db import models

from users.models.buyer import *
from users.models.seller import *

from .order import *
from .orderItem import *
from .subOrder import *

from scripts.utils import validate_date
from decimal import Decimal


class OrderShipment(models.Model):

    suborder = models.ForeignKey(SubOrder)

    pickup_address = models.ForeignKey(SellerAddress)
    drop_address = models.ForeignKey(BuyerAddress)

    invoice_number = models.CharField(max_length=50, blank=True)
    invoice_date = models.DateTimeField(blank=True, null=True)

    logistics_partner = models.CharField(max_length=50, blank=True,null=True)
    waybill_number = models.CharField(max_length=50, blank=True,null=True)

    packaged_weight = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    packaged_length = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    packaged_breadth = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    packaged_height = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)

    cod_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)

    remarks = models.TextField(blank=True)

    current_status = models.IntegerField(default=0)

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

    def __unicode__(self):
        return str(self.suborder.id)

def validateOrderShipmentData(orderShipment):

    flag = True

    if not "invoice_number" in orderShipment or orderShipment["invoice_number"]==None:
        orderShipment["invoice_number"] = ""
    if not "invoice_date" in orderShipment or orderShipment["invoice_date"]==None or not validate_date(orderShipment["invoice_date"]):
        flag = False
    if not "logistics_partner" in orderShipment or orderShipment["logistics_partner"]==None:
        orderShipment["logistics_partner"] = "Fedex"
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
    
    return flag



def populateOrderShipment(OrderShipmentPtr, orderShipment):
    OrderShipmentPtr.invoice_number = orderShipment["invoice_number"]
    OrderShipmentPtr.invoice_date = orderShipment["invoice_date"]
    OrderShipmentPtr.logistics_partner = orderShipment["logistics_partner"]
    OrderShipmentPtr.waybill_number = orderShipment["waybill_number"]
    OrderShipmentPtr.packaged_weight = Decimal(orderShipment["packaged_weight"])
    OrderShipmentPtr.packaged_length = Decimal(orderShipment["packaged_length"])
    OrderShipmentPtr.packaged_breadth = Decimal(orderShipment["packaged_breadth"])
    OrderShipmentPtr.packaged_height = Decimal(orderShipment["packaged_height"])
    OrderShipmentPtr.cod_charge = Decimal(orderShipment["cod_charge"])
    OrderShipmentPtr.shipping_charge = Decimal(orderShipment["shipping_charge"])
    OrderShipmentPtr.remarks = orderShipment["remarks"]
    OrderShipmentPtr.rto_remarks = orderShipment["rto_remarks"]
    OrderShipmentPtr.tracking_url = orderShipment["tracking_url"]

OrderShipmentStatus = {
    1:"Shipment created",
    2:"3PL notified",
    3:"3PL manifested",
    4:"3PL in transit",
    5:"3PL stuck in transit",
    6:"Delivered",
    7:"RTO in transit",
    8:"RTO delivered",
    9:"Lost"
}

