from django.db import models

from .country import Country

class State(models.Model):

	country = models.ForeignKey('address.Country',blank=True, null=True, on_delete=models.SET_NULL)

	name = models.CharField(max_length=50, blank=False)
	short_form = models.CharField(max_length=10, blank=True)
	is_union_territory = models.BooleanField(default=False)
	capital = models.CharField(max_length=50, blank=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		default_related_name = "state"
		verbose_name="State"
		verbose_name_plural = "States"

	def __unicode__(self):
		return "{} - {}".format(self.id,self.name)

def filterState(stateParameters):
	states = State.objects.all()
	return states