from django.db import models

class FAQEntry(models.Model):

	topic = models.CharField(max_length = 100,blank=True)

	question = models.TextField(blank=True)
	answer = models.TextField(blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return "{} - {}".format(self.topic,self.question)