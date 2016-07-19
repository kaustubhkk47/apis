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

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		default_related_name = "pincodeserviceability"
		verbose_name="Pincode Serviceability"
		verbose_name_plural = "Pincode Serviceability"

	def __unicode__(self):
		return "{} - {} - Regular Delivery Available: {}".format(self.pincode.pincode,self.logistics_partner.name,self.regular_delivery_available)

class PincodeServiceabilityAdmin(admin.ModelAdmin):
	search_fields = ["pincode__pincode"]
	list_display = ["id", "link_to_pincode", "logistics_partner", "regular_delivery_available", "cod_available"]
	list_filter = ["logistics_partner", "regular_delivery_available", "cod_available"]

	list_display_links = ["id", "link_to_pincode"]

	def link_to_pincode(self, obj):
		return link_to_foreign_key(obj, "pincode")
	link_to_pincode.short_description = "Pincode"
	link_to_pincode.allow_tags=True