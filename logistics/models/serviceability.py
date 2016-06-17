from django.db import models

from .logisticspartner import LogisticsPartner
from address.models.pincode import Pincode

class PincodeServiceability(models.Model):

	logistics_partner = models.ForeignKey(LogisticsPartner)
	pincode = models.ForeignKey(Pincode)

	delivery_available = models.BooleanField(default=False)
	pickup_available = models.BooleanField(default=False)

	regular_delivery_available = models.BooleanField(default=False)
	regular_pickup_available = models.BooleanField(default=False)
	cod_available = models.BooleanField(default=False)

	def __unicode__(self):
		return str(self.id) + " - " + self.pincode.pincode + " - delivery: " + self.delivery_available