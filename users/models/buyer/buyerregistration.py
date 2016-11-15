from django.db import models
from django.contrib import admin

from scripts.utils import *

from general.models.smssent import send_sms

import random

from datetime import timedelta

class BuyerRegistration(models.Model):

	email = models.EmailField(max_length=255, blank=True, null = True)
	mobile_number = models.CharField(max_length=11, blank=False)
	password = models.CharField(max_length=255, blank=True)

	otp_number = models.CharField(max_length=10, blank=True)
	messages_sent = models.IntegerField(default=0)

	is_active = models.BooleanField(default=True)
	verification_attempts = models.IntegerField(default=0)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name="Buyer Registration"
		verbose_name_plural = "Buyer Registrations"

	def __unicode__(self):
		return "{} - {}".format(self.id, self.mobile_number)

	def populateBuyerRegistration(self,  buyer):
		self.email = buyer["email"]
		self.mobile_number = buyer["mobile_number"]
		self.password = buyer["password"]
		self.otp_number = "{0:06d}".format(random.randint(0, 999999))

	def sendVerificationSMS(self):
		message_text = "OTP is {} for registration on Wholdus.com. Use it to complete registration process".format(self.otp_number)
		send_sms(message_text, self.mobile_number, "buyer", "Registration OTP")
		self.messages_sent += 1
		self.save()

	def getExpiryTimeStamp(self):
		return getTimeStamp(self.created_at + timedelta(minutes=15))

	def fillBuyerData(self, buyer):
		buyer["email"] = self.email
		buyer["mobile_number"] = self.mobile_number
		buyer["password"] = self.password
		buyer["whatsapp_number"] = self.mobile_number
		buyer["mobile_verification"] = 1
		buyer["email_verification"] = 1

class BuyerRegistrationAdmin(admin.ModelAdmin):

	list_display = ["id", "email", "mobile_number", "created_at_ist"]

	def created_at_ist(self, obj):
		return time_in_ist(obj.created_at)

def validateBuyerRegistrationData(buyer):

	if not "password" in buyer or not validate_password(buyer["password"]):
		return False
	if not "mobile_number" in buyer or not validate_mobile_number(buyer["mobile_number"]):
		return False
	if not "email" in buyer or buyer["email"]==None or not validate_email(buyer["email"]):
		return False

	return True

def validateBuyerRegistrationResendSMSData(buyer):
	if not "registration_token" in buyer or buyer["registration_token"]==None:
		return False
	return True

def validateBuyerRegistrationVerifyData(buyer):
	if not "registration_token" in buyer or buyer["registration_token"]==None:
		return False
	if not "otp_number" in buyer or buyer["otp_number"]==None:
		return False
	return True

def getBuyerRegistrationFromToken(registration_token):

	tokenPayload = check_token_validity(registration_token)

	tokenDetails = {}

	tokenDetails[0] = True
	tokenDetails[1] = customResponse(400, error_code=6, error_details=  "Invalid data for buyer registration sent")

	if not "sub" in tokenPayload or not tokenPayload["sub"] == "buyer registration":
		tokenDetails[0] = False
	if not "exp" in tokenPayload or not checkTokenTimeValidity(tokenPayload["exp"]):
		tokenDetails[0] = False
		tokenDetails[1] = customResponse(403, error_code=10, error_details=  "Token expired")
	if not "jti" in tokenPayload or not validate_integer(tokenPayload["jti"]):
		tokenDetails[0] = False
	else:
		BuyerRegistrationPtr = BuyerRegistration.objects.filter(id=int(tokenPayload["jti"]), is_active=True)

		if len(BuyerRegistrationPtr) == 0:
			tokenDetails[0] = False	
		else:
			BuyerRegistrationPtr = BuyerRegistrationPtr[0]
			tokenDetails[1] = BuyerRegistrationPtr

	return tokenDetails

