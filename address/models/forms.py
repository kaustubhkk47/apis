from django.db import models
from django.contrib import admin
from scripts.utils import link_to_foreign_key

#from .state import State


class Form(models.Model):

	state = models.ForeignKey('address.State',blank=True, null=True)

	name = models.CharField(max_length=200, blank=False, null = True)

	## form_type: 1 - inbound movement
	form_type = models.IntegerField(default=1)

	## form_type: 1 - offline; 2 - online; 3 - both
	availability = models.IntegerField(default=1)

	is_b2b = models.BooleanField(default=1)

	min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	max_amount = models.DecimalField(max_digits=10, decimal_places=2, default=9999999999)

	class Meta:
		verbose_name="Form"
		verbose_name_plural = "Forms"

	def __unicode__(self):
		return "{} - {}".format(self.id,self.name)

class FormAdmin(admin.ModelAdmin):
	list_display = ["id", "name", "link_to_state","min_amount","availability"]
	list_filter = ["state"]

	list_display_links = ["name","link_to_state"]
	def link_to_state(self, obj):
		return link_to_foreign_key(obj, "state")
	link_to_state.allow_tags=True
	link_to_state.short_description = "State"