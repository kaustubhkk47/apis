from django.db import models
from django.contrib import admin
from scripts.utils import link_to_foreign_key

from .city import City

class Pincode(models.Model):

	city = models.ForeignKey('address.City',blank=True, null=True, on_delete=models.SET_NULL)

	pincode = models.CharField(max_length=15, blank=False, db_index=True)
	city_name = models.CharField(max_length=50, blank=False)
	state_name = models.CharField(max_length=50, blank=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		default_related_name = "pincode"
		verbose_name="Pincode"
		verbose_name_plural = "Pincodes"

	def __unicode__(self):
		return "{} - {} - {}".format(self.pincode,self.city_name,self.state_name)

class PincodeAdmin(admin.ModelAdmin):
	search_fields = ["pincode", "city_name", "state_name"]
	list_display = ["pincode", "link_to_city", "state_name"]

	list_display_links = ["pincode","link_to_city"]
	def link_to_city(self, obj):
		return link_to_foreign_key(obj, "city")
	link_to_city.short_description = "City"
	
	link_to_city.allow_tags=True