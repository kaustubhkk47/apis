from django.db import models

from .city import City

class Pincode(models.Model):

	city = models.ForeignKey('address.City',blank=True, null=True)

	pincode = models.CharField(max_length=15, blank=False)
	city_name = models.CharField(max_length=50, blank=False)
	state_name = models.CharField(max_length=50, blank=False)

	def __unicode__(self):
		return str(self.id) + " - " + self.pincode + " - " + self.city_name + " - " + self.state_name