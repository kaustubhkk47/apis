from django.db import models

from .country import Country

class State(models.Model):

	country = models.ForeignKey(Country,blank=True, null=True)

	name = models.CharField(max_length=50, blank=False)
	short_form = models.CharField(max_length=10, blank=True)
	is_union_territory = models.BooleanField(default=False)
	capital = models.CharField(max_length=50, blank=False)

	def __unicode__(self):
		return str(self.id) + " - " + self.name

def filterState(stateParameters):
	states = State.objects.all()
	return states