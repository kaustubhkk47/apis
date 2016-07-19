from django.db import models
from django.contrib import admin

class Country(models.Model):

	name = models.CharField(max_length=50, blank=False)

	a2_iso_code = models.CharField(max_length=10, blank=True)
	a3_un_code = models.CharField(max_length=10, blank=True)
	num_un_code = models.CharField(max_length=10, blank=True)
	dialing_code = models.CharField(max_length=20, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		default_related_name = "country"
		verbose_name="Country"
		verbose_name_plural = "Countries"

	def __unicode__(self):
		return "{} - {}".format(self.id,self.name)

class CountryAdmin(admin.ModelAdmin):
	list_display = ["id", "name"]
	search_fields = ["name"]