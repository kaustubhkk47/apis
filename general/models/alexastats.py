from django.db import models
from django.contrib import admin

class AlexaStats(models.Model):

	global_rank = models.IntegerField(default=0)
	india_rank = models.IntegerField(default=0)
	bounce_rate = models.CharField(max_length = 20,blank=True)
	daily_page_views_per_visitor = models.CharField(max_length = 20,blank=True)
	daily_time_on_site = models.CharField(max_length = 20,blank=True)
	search_visits = models.CharField(max_length = 20,blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name="Alexa Stats"
		verbose_name_plural = "Alexa Stats"

	def __unicode__(self):
		return "{} - {} - {}".format(self.id,self.created_at,self.india_rank)

class AlexaStatsAdmin(admin.ModelAdmin):
	list_display = ["id","created_at", "global_rank", "india_rank", "bounce_rate", "daily_page_views_per_visitor", "daily_time_on_site"]