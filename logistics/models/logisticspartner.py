from django.db import models

class LogisticsPartner(models.Model):

	name = models.CharField(max_length=50, blank=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		default_related_name = "logisticspartner"
		verbose_name="Logistics Partner"
		verbose_name_plural = "Logistics Partners"

	def __unicode__(self):
		return "{} - {}".format(self.id,self.name)