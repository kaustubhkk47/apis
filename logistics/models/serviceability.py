from django.db import models
from django.contrib import admin

from .logisticspartner import LogisticsPartner
from address.models.pincode import Pincode

from scripts.utils import link_to_foreign_key

class PincodeServiceability(models.Model):

	logistics_partner = models.ForeignKey('logistics.LogisticsPartner')
	pincode = models.ForeignKey('address.Pincode')

	delivery_available = models.BooleanField(default=False)
	pickup_available = models.BooleanField(default=False)

	regular_delivery_available = models.BooleanField(default=False)
	regular_pickup_available = models.BooleanField(default=False)
	cod_available = models.BooleanField(default=False)

	ou_code = models.CharField(max_length=15, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		default_related_name = "pincodeserviceability"
		verbose_name="Pincode Serviceability"
		verbose_name_plural = "Pincode Serviceability"

	def __unicode__(self):
		return "{} - {} - Regular Delivery Available: {}".format(self.pincode.pincode,self.logistics_partner.name,self.regular_delivery_available)

class PincodeServiceabilityAdmin(admin.ModelAdmin):
	search_fields = ["pincode__pincode", "pincode__city_name", "pincode__state_name"]
	list_display = ["id", "link_to_pincode", "logistics_partner", "regular_delivery_available", "cod_available", "ou_code"]
	list_filter = ["logistics_partner", "regular_delivery_available", "cod_available"]

	list_display_links = ["id", "link_to_pincode"]

	def link_to_pincode(self, obj):
		return link_to_foreign_key(obj, "pincode")
	link_to_pincode.short_description = "Pincode"
	link_to_pincode.allow_tags=True

def filterServiceablePincodes(parameters):

	serviceablePincodes = PincodeServiceability.objects.all()

	if "pincodesArr" in parameters:
		serviceablePincodes = serviceablePincodes.filter(pincode_id__in=parameters["pincodesArr"])

	if "pincodesCodesArr" in parameters:
		serviceablePincodes = serviceablePincodes.filter(pincode__pincode__in=parameters["pincodesCodesArr"])

	if "logisticsPartnersArr" in parameters:
		serviceablePincodes = serviceablePincodes.filter(logistics_partner_id__in=parameters["logisticsPartnersArr"])

	if "regular_delivery_available" in parameters:
		serviceablePincodes = serviceablePincodes.filter(regular_delivery_available=parameters["regular_delivery_available"])

	if "regular_pickup_available" in parameters:
		serviceablePincodes = serviceablePincodes.filter(regular_pickup_available=parameters["regular_pickup_available"])

	if "cod_available" in parameters:
		serviceablePincodes = serviceablePincodes.filter(cod_available=parameters["cod_available"])

	return serviceablePincodes