from django.db import models
from django.contrib import admin
from scripts.utils import link_to_foreign_key

from .state import State

class City(models.Model):

	state = models.ForeignKey('address.State',blank=True, null=True, on_delete=models.SET_NULL)

	name = models.CharField(max_length=50, blank=False)
	state_name = models.CharField(max_length=50, blank=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		default_related_name = "city"
		verbose_name="City"
		verbose_name_plural = "Cities"

	def __unicode__(self):
		return "{} - {}".format(self.id,self.name)

class CityAdmin(admin.ModelAdmin):
	list_display = ["id", "name", "link_to_state"]
	list_filter = ["state"]
	search_fields = ["name"]

	list_display_links = ["name","link_to_state"]
	def link_to_state(self, obj):
		return link_to_foreign_key(obj, "state")
	link_to_state.allow_tags=True
	link_to_state.short_description = "State"