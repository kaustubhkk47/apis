from django.db import models
from django.contrib import admin
from users.models.buyer import BuyerAddress
from users.models.seller import SellerAddress

from .orderItem import OrderItem

from scripts.utils import validate_date, validate_number, validate_bool, validate_integer, link_to_foreign_key, generate_pdf
from decimal import Decimal
from django.utils import timezone

from logistics.models.logisticspartner import LogisticsPartner

from users.serializers.seller import serialize_seller_address
from users.serializers.buyer import serialize_buyer_address

import settings


class OrderShipment(models.Model):

	suborder = models.ForeignKey('orders.SubOrder')

	pickup_address = models.ForeignKey('users.SellerAddressHistory', blank=True, null=True)
	drop_address = models.ForeignKey('users.BuyerAddressHistory', blank=True, null=True)

	invoice_number = models.CharField(max_length=50, blank=True)
	invoice_date = models.DateTimeField(blank=True, null=True)

	logistics_partner = models.ForeignKey('logistics.LogisticsPartner', blank=True, null =True)
	logistics_partner_name = models.CharField(max_length=50, blank=True, default="")
	waybill_number = models.CharField(max_length=50, blank=True, default="")

	packaged_weight = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	packaged_length = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	packaged_breadth = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	packaged_height = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)

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

	tracking_url = models.URLField(blank=True, default="")

	rto_remarks = models.TextField(blank=True, default="")

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	manifest_link = models.TextField(blank=True)

	class Meta:
		ordering = ["-id"]
		default_related_name = "ordershipment"
		verbose_name="Order Shipment"
		verbose_name_plural = "Order Shipments"

	def __unicode__(self):
		return "{} - {} - {}".format(self.id,self.suborder.display_number,self.suborder.seller.name)

	def create_manifest(self):

		manifest_dict = {}
		manifest_dict["orderItems"] = []
		manifest_dict["extra_order_items"] = 0
		maxOrderItems = 15

		subOrderPtr = self.suborder

		buyerPtr = subOrderPtr.order.buyer
		sellerPtr = subOrderPtr.seller

		sellerAddressPtr = subOrderPtr.seller_address_history

		buyerAddressPtr = subOrderPtr.order.buyer_address_history

		allOrderItems = OrderItem.objects.filter(order_shipment_id=self.id)

		orderItemCount = len(allOrderItems)

		extraOrderItems = orderItemCount - maxOrderItems

		if extraOrderItems > 0:
			manifest_dict["extra_order_items"] = extraOrderItems
			orderItemCount = maxOrderItems

		for i in range(orderItemCount):

			orderItemPtr = allOrderItems[i]
			manifestOrderItem = {
				"name":orderItemPtr.product.display_name,
				"pieces":orderItemPtr.pieces
			}

			manifest_dict["orderItems"].append(manifestOrderItem)

		outputLink = "media/generateddocs/shipmentmanifest/{}/{}/".format(sellerPtr.id,subOrderPtr.display_number) 
		outputDirectory = settings.STATIC_ROOT + outputLink
		outputFileName = "WholdusManifest-{}-{}.pdf".format(self.id,subOrderPtr.display_number)

		self.manifest_link = outputLink + outputFileName
		self.save()

		manifest_dict["order"] = {
			"display_number": subOrderPtr.display_number
		}

		manifest_dict["buyer"] = {
			"name": buyerPtr.name
		}

		manifest_dict["buyer_address"] = serialize_buyer_address(buyerAddressPtr)

		manifest_dict["seller"] = {
			"name": sellerPtr.name,
			"company_name": sellerPtr.company_name,
			"vat_tin": sellerPtr.sellerdetails.vat_tin
		}

		manifest_dict["seller_address"] = serialize_seller_address(sellerAddressPtr)

		manifest_dict["shipment"] = {
			"waybill_number": self.waybill_number,
			"shipping_amount": '{0:.0f}'.format(self.cod_charge + self.shipping_charge),
			"logistics_partner": self.logistics_partner_name,
			"invoice_number": self.invoice_number,
			"final_price": '{0:.0f}'.format(self.final_price),
			"amount_to_collect":'{0:.0f}'.format(float(self.cod_charge) + float(self.shipping_charge) + float(self.final_price)),
			"packaged_length": '{0:.0f}'.format(self.packaged_length),
			"packaged_breadth": '{0:.0f}'.format(self.packaged_breadth),
			"packaged_height": '{0:.0f}'.format(self.packaged_height),
			"packaged_weight": '{0:.2f}'.format(self.packaged_weight)
		}

		
		template_file = "manifest/shipment_manifest.html"

		generate_pdf(template_file, manifest_dict, outputDirectory, outputFileName)

class OrderShipmentAdmin(admin.ModelAdmin):
	search_fields = ["suborder__display_number"]
	list_display = ["id","waybill_number", "link_to_suborder", "link_to_pickup_address", "link_to_drop_address", "final_price"]

	list_display_links = ["waybill_number","link_to_suborder", "link_to_pickup_address", "link_to_drop_address"]

	list_filter = ["current_status"]

	def link_to_suborder(self, obj):
		return link_to_foreign_key(obj, "suborder")
	link_to_suborder.short_description = "Suborder"
	link_to_suborder.allow_tags=True

	def link_to_pickup_address(self, obj):
		return link_to_foreign_key(obj, "pickup_address")
	link_to_pickup_address.short_description = "Pickup Address"
	link_to_pickup_address.allow_tags=True

	def link_to_drop_address(self, obj):
		return link_to_foreign_key(obj, "drop_address")
	link_to_drop_address.short_description = "Drop Address"
	link_to_drop_address.allow_tags=True

def validateOrderShipmentData(orderShipment):

	flag = True

	if not "invoice_number" in orderShipment or orderShipment["invoice_number"]==None:
		orderShipment["invoice_number"] = ""
	if not "invoice_date" in orderShipment or orderShipment["invoice_date"]==None or not validate_date(orderShipment["invoice_date"]):
		return False
	if not "waybill_number" in orderShipment or orderShipment["waybill_number"]==None:
		orderShipment["waybill_number"] = ""
	if not "packaged_weight" in orderShipment or not validate_number(orderShipment["packaged_weight"]):
		return False
	if not "packaged_length" in orderShipment or not validate_number(orderShipment["packaged_length"]):
		return False
	if not "packaged_breadth" in orderShipment or not validate_number(orderShipment["packaged_breadth"]):
		return False
	if not "packaged_height" in orderShipment  or not validate_number(orderShipment["packaged_height"]):
		return False
	if not "cod_charge" in orderShipment or not validate_number(orderShipment["cod_charge"]):
		return False
	if not "shipping_charge" in orderShipment or not validate_number(orderShipment["shipping_charge"]):
		return False
	if not "remarks" in orderShipment or orderShipment["remarks"]==None:
		orderShipment["remarks"] = ""
	if not "rto_remarks" in orderShipment or orderShipment["rto_remarks"]==None:
		orderShipment["rto_remarks"] = ""
	if not "tracking_url" in orderShipment or orderShipment["tracking_url"]==None:
		orderShipment["tracking_url"] = ""
	if not "all_items" in orderShipment or not validate_bool(orderShipment["all_items"]):
		return False
	if not "logistics_partner" in orderShipment or orderShipment["logistics_partner"]==None:
		return False
	else:
		try:
			logistics_partner = LogisticsPartner.objects.get(name=orderShipment["logistics_partner"])
		except Exception as e:
			return False
	
	return flag

def populateOrderShipment(OrderShipmentPtr, orderShipment):
	OrderShipmentPtr.invoice_number = orderShipment["invoice_number"]
	OrderShipmentPtr.invoice_date = orderShipment["invoice_date"]
	logistics_partner = LogisticsPartner.objects.get(name=orderShipment["logistics_partner"])
	OrderShipmentPtr.logistics_partner_name = logistics_partner.name
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
	if logistics_partner.id == 1:
		OrderShipmentPtr.tracking_url = "https://www.fedex.com/apps/fedextrack/?action=track&trackingnumber="+orderShipment["waybill_number"]+"&cntry_code=in"
	else:
		OrderShipmentPtr.tracking_url = "http://www.gati.com/gatitrck.jsp?dktNo={}".format(orderShipment["waybill_number"])
	OrderShipmentPtr.current_status = 3
	OrderShipmentPtr.tpl_manifested_time = timezone.now()

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

def validateOrderShipmentItemsData(orderItems, sentOrderItems):

	for orderItem in orderItems:

		if not "orderitemID" in orderItem or not validate_integer(orderItem["orderitemID"]):
			return False

		sentOrderItems.append(int(orderItem["orderitemID"]))

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