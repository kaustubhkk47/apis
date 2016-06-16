from django.db import models

class Country(models.Model):

	name = models.CharField(max_length=50, blank=False)

	a2_iso_code = models.CharField(max_length=10, blank=True)
	a3_un_code = models.CharField(max_length=10, blank=True)
	num_un_code = models.CharField(max_length=10, blank=True)
	dialing_code = models.CharField(max_length=20, blank=True)

	def __unicode__(self):
		return self.name