from django.db import models
from django.contrib import admin
from django.utils import timezone
import settings
from scripts.utils import create_email
import time

class MarketingEmail(models.Model):

	email = models.EmailField(max_length=255, blank=True, null=True)
	contact_name = models.CharField(max_length=100, blank=True)

	message_sent_time = models.DateTimeField(null=True, blank=True)
	message_sent_count = models.IntegerField(default=0)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	unsubscribed = models.BooleanField(default=False)

	class Meta:
		verbose_name="Marketing Email"
		verbose_name_plural = "Marketing Email"

	def __unicode__(self):
		return "{} - {}".format(self.email,self.contact_name)

class MarketingEmailAdmin(admin.ModelAdmin):
	list_display = ["id", "email", "contact_name", "message_sent_count", "unsubscribed"]
	list_filter = ["message_sent_count"]
	search_fields = ["id", "email", "contact_name"]

def filterMarketingEmails(parameters):

	marketingEmails = MarketingEmail.objects.filter(unsubscribed=False, message_sent_count=0)

	return marketingEmails

def sendMarketingEmails(marketingEmailPtr):
	from_email = "Wholdus <mailer@wholdus.com>"
	mail_template_file = "marketing/app_marketing.html"

	for marketingEmail in marketingEmailPtr:
		mail_dict = {}
		time.sleep(0.1)
		to = [marketingEmail.email]
		subject = "{}, Buy Ladies Apparel At Manufacturer Prices!".format(marketingEmail.contact_name)
		mail_dict["unsubscribe_link"] = "{}/general/marketingemail/unsubscribe/?marketingemailID={}".format(settings.API_BASE_URL, marketingEmail.id)
		create_email(mail_template_file,mail_dict, subject, from_email, to)
		marketingEmail.message_sent_count += 1
		marketingEmail.message_sent_time = timezone.now()
		marketingEmail.save()