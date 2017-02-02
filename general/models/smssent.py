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
	message_count = models.IntegerField(default=1)

	test_sms = models.BooleanField(default=0)

	sending_success = models.BooleanField(default=0)
	error_message = models.TextField(blank=True)
	error_code = models.CharField(max_length = 30, blank=True)

	delivered = models.BooleanField(default=0)
	delivered_time = models.DateTimeField(blank=True, null=True)
	delivery_status = models.CharField(max_length = 10,blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	service_provider = models.CharField(max_length = 50,blank=True)

	class Meta:
		verbose_name="SMSSent"
		verbose_name_plural = "SMSSent"

	def __unicode__(self):
		return "{} - {}".format(self.id,self.mobile_number)

class SMSSentAdmin(admin.ModelAdmin):

	search_fields = ["mobile_number"]
	list_display = ["id","mobile_number", "user_type", "sms_purpose", "created_at_ist", "delivered"]

	list_filter = ["user_type", "sms_purpose", "delivered"]

	def created_at_ist(self, obj):
		return time_in_ist(obj.created_at)

def send_sms(message_text, mobile_number, user_type, sms_purpose):
	url = "http://api.textlocal.in/send/"
	apiKey = "VAWHxD4nf9U-8LcsDTXDL5iMOmSicSvlLiRHw9rJZ0"

	deliveryBaseUrl = settings.API_BASE_URL + "/general/sentsms/deliveryreport/"

	data = {}
	data["apiKey"] = apiKey
	data["sender"] = "WHOLDS"
	
	data["message"] = message_text

	numbers = "91{}".format(mobile_number)

	data["numbers"] = numbers

	newSMSSent = SMSSent()
	newSMSSent.mobile_number = mobile_number
	newSMSSent.user_type = user_type
	newSMSSent.sms_purpose = sms_purpose
	newSMSSent.message_text = message_text
	newSMSSent.service_provider = "TextLocal"
	newSMSSent.save()

	if not settings.CURRENT_ENVIRONMENT == 'prod':
		data["test"] = True
		newSMSSent.test_sms = 1

	data["receipt_url"] = deliveryBaseUrl
	data["custom"] = newSMSSent.id

	response = requests.post(url, data)

	if response.status_code == 200:

		try:
			responseJson = response.json()
		except Exception as e:
			newSMSSent.error_message = "Could not parse response json" 
		else:
			if responseJson["status"] == "success":
				newSMSSent.sending_success = 1
				newSMSSent.message_count =int(responseJson["num_messages"])
			elif responseJson["status"] == "failure":
				error_message = ""
				error_code = ""
				for errorobject in responseJson["errors"]:
					error_message += str(errorobject["message"]) + ","
					error_code += str(errorobject["code"]) + ","
				newSMSSent.error_message = error_message
				newSMSSent.error_code = error_code
			else:
				newSMSSent.error_message = "Unknown error" 
	else:
		newSMSSent.error_message = "Response status code was not 200" 

	newSMSSent.save()


def validateSmsSentData(delivery_report):

	if not "status" in delivery_report or delivery_report["status"] == None:
		return False
	#if not "datetime" in delivery_report or delivery_report["datetime"] == None:
	#	return False

	return True