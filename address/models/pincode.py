from django.db import models

class Pincode(models.Model):

	code = models.CharField(max_length=10, blank=False)

	def __unicode__(self):
        return self.code