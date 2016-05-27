from django.db import models

from users.models.buyer import *
from users.models.seller import *

from .order import *
from .orderItem import *
from .subOrder import *


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
