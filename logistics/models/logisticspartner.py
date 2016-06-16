from django.db import models

class LogisticsPartner(models.Model):

	name = models.CharField(max_length=50, blank=False)

	def __unicode__(self):
		return str(self.id) + " - " + self.name