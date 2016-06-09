from django.db import models

class State(models.Model):

	name = models.CharField(max_length=50, blank=False)

	def __unicode__(self):
        return self.name