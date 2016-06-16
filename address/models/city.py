from django.db import models

from .state import State

class City(models.Model):

	state = models.ForeignKey(State,blank=True, null=True)

	name = models.CharField(max_length=50, blank=False)
	state_name = models.CharField(max_length=50, blank=False)

	def __unicode__(self):
		return str(self.id) + " - " + self.name + " - " + self.state_name 