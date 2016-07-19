from django.db import models
from django.contrib import admin

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
		return "{} - {} - {}".format(self.id,self.name,self.state_name)

