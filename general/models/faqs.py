from django.db import models

class FAQEntry(models.Model):

	topic = models.CharField(max_length = 100,blank=True)

	question = models.TextField(blank=True)
	answer = models.TextField(blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name="FAQ Entry"
		verbose_name_plural = "FAQ Entries"

	def __unicode__(self):
		return "{} - {}".format(self.topic,self.question)

class TermsAndConditions(models.Model):

	text = models.TextField(blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name="Terms and Conditions"
		verbose_name_plural = "Terms and Conditions"

	def __unicode__(self):
		return "{}".format(self.text)

class AboutUs(models.Model):

	text = models.TextField(blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name="About Us"
		verbose_name_plural = "About Us"

	def __unicode__(self):
		return "{}".format(self.text)

class PrivacyPolicy(models.Model):

	text = models.TextField(blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name="Privacy Policy"
		verbose_name_plural = "Privacy Policy"

	def __unicode__(self):
		return "{}".format(self.text)