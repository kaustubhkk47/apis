from django.db import models
from django.contrib import admin

from scripts.utils import time_in_ist

import settings
import requests

class  SMSSent(models.Model):

	mobile_number = models.CharField(max_length=11, blank=False)

	user_type = models.CharField(max_length = 30,blank=True)
	sms_purpose = models.CharField(max_length = 50,blank=True)

	message_text = models.TextField(blank=True)

	test_sms = models.BooleanField(default=0)

	delivered = models.BooleanField(default=0)
	delivered_time = models.DateTimeField(blank=True, null=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	service_provider = models.CharField(max_length = 50,blank=True)

	class Meta:
		verbose_name="SMSSent"
		verbose_name_plural = "SMSSent"

	def __unicode__(self):
		return "{} - {}".format(self.id,self.mobile_number)

class SMSSentAdmin(admin.ModelAdmin):
	list_display = ["id","mobile_number", "user_type", "sms_purpose", "created_at_ist", "delivered"]

	list_filter = ["user_type", "sms_purpose", "delivered"]

	def created_at_ist(self, obj):
		return time_in_ist(obj.created_at)

def send_sms(message_text, mobile_number, user_type, sms_purpose):
	url = "http://api.textlocal.in/send/"
	apiKey = "VAWHxD4nf9U-8LcsDTXDL5iMOmSicSvlLiRHw9rJZ0"

	data = {}
	data["apiKey"] = apiKey
	data["sender"] = "TXTLCL"
	
	data["message"] = message_text

	numbers = "91{}".format(mobile_number)

	data["numbers"] = numbers

	newSMSSent = SMSSent()
	newSMSSent.mobile_number = mobile_number
	newSMSSent.user_type = user_type
	newSMSSent.sms_purpose = sms_purpose
	newSMSSent.message_text = message_text
	newSMSSent.service_provider = "TextLocal"

	if not settings.CURRENT_ENVIRONMENT == 'prod':
		data["test"] = True
		newSMSSent.test_sms = 1

	r = requests.post(url, data)

	if r.status_code == 200:

		try:
			responseJson = r.json()
		except Exception as e:
			pass
		else:
			if responseJson["status"] == "success":

				newSMSSent.save()