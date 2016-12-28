from django.db import models
from django.contrib import admin

from scripts.utils import *

from datetime import timedelta

import random

from general.models.smssent import send_sms

class BuyerRefreshToken(models.Model):

	buyer = models.ForeignKey('users.Buyer')

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	is_active = models.BooleanField(default=True)

	class Meta:
		verbose_name="Buyer Refresh Token"
		verbose_name_plural = "Buyer Refresh Tokens"

	def __unicode__(self):
		return "{}".format(self.buyer)

	def getExpiryTimeStamp(self):
		return getTimeStamp(self.created_at + timedelta(days=60))

	def populateFromBuyer(self, buyerPtr):
		self.buyer = buyerPtr

class BuyerRefreshTokenAdmin(admin.ModelAdmin):

	list_display = ["id", "link_to_buyer", "created_at_ist"]

	def created_at_ist(self, obj):
		return time_in_ist(obj.created_at)

	def link_to_buyer(self, obj):
		return link_to_foreign_key(obj, "buyer")
	link_to_buyer.short_description = "Buyer"
	link_to_buyer.allow_tags=True

class BuyerAccessToken(models.Model):

	buyer = models.ForeignKey('users.Buyer')
	buyer_refresh_token = models.ForeignKey('users.BuyerRefreshToken')

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name="Buyer Access Token"
		verbose_name_plural = "Buyer Access Tokens"

	def __unicode__(self):
		return "{}".format(self.buyer)

	def getExpiryTimeStamp(self):
		# TODO: Change expiry time of buyer access token
		return getTimeStamp(self.created_at + timedelta(days=30))

	def populateFromRefreshToken(self, buyerRefreshToken):
		self.buyer_id = buyerRefreshToken.buyer_id
		self.buyer_refresh_token = buyerRefreshToken

class BuyerAccessTokenAdmin(admin.ModelAdmin):

	list_display = ["id", "link_to_buyer", "created_at_ist"]

	def created_at_ist(self, obj):
		return time_in_ist(obj.created_at)

	def link_to_buyer(self, obj):
		return link_to_foreign_key(obj, "buyer")
	link_to_buyer.short_description = "Buyer"
	link_to_buyer.allow_tags=True

class BuyerForgotPasswordToken(models.Model):

	mobile_number = models.CharField(max_length=11, blank=False)

	is_active = models.BooleanField(default=True)
	verification_attempts = models.IntegerField(default=0)

	otp_number = models.CharField(max_length=10, blank=True)
	messages_sent = models.IntegerField(default=0)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name="Buyer Forgot Password Token"
		verbose_name_plural = "Buyer Forgot Password Tokens"

	def __unicode__(self):
		return "{}".format(self.mobile_number)

	def getExpiryTimeStamp(self):
		return getTimeStamp(self.created_at + timedelta(minutes=10))

	def populateBuyerBuyerForgotPasswordToken(self,  buyer):
		self.mobile_number = buyer["mobile_number"]
		self.otp_number = "{0:06d}".format(random.randint(0, 999999))

	def sendVerificationSMS(self):
		message_text = "Use {} as OTP to change you password on Wholdus.com. Please don't share OTP with anyone".format(self.otp_number)
		send_sms(message_text, self.mobile_number, "buyer", "Forgot Password OTP")
		self.messages_sent += 1
		self.save()

class BuyerForgotPasswordTokenAdmin(admin.ModelAdmin):

	list_display = ["id", "mobile_number", "created_at_ist"]

	def created_at_ist(self, obj):
		return time_in_ist(obj.created_at)

class BuyerFireBaseToken(models.Model):
	buyer = models.ForeignKey('users.Buyer', null = True, blank = True)

	instance_id = models.CharField(max_length=255, blank=True, null = True)
	token = models.CharField(max_length=255, blank=True, null = True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name="Buyer FireBase Token"
		verbose_name_plural = "Buyer FireBase Tokens"

	def __unicode__(self):
		return "{}".format(self.buyer)

	@staticmethod
	def validateBuyerFireBaseTokenData(data):
		if not "instance_id" in data or data["instance_id"] == None or data["instance_id"] == "":
			return False
		if not "token" in data or data["token"] == None or data["token"] == "":
			return False
		return True


def validateBuyerAccessToken(accessToken):

	tokenPayload = get_token_payload(accessToken, "buyerID")

	if not "sub" in tokenPayload or not tokenPayload["sub"] == "buyer access token":
		tokenPayload = {}
	#if not "exp" in tokenPayload or not checkTokenTimeValidity(tokenPayload["exp"]):
	#	tokenPayload = {}
	if not "jti" in tokenPayload or not validate_integer(tokenPayload["jti"]):
		tokenPayload = {}

	return tokenPayload

def validateBuyerRefreshToken(accessToken):

	tokenPayload = get_token_payload(accessToken, "buyerID")

	if not "sub" in tokenPayload or not tokenPayload["sub"] == "buyer refresh token":
		tokenPayload = {}
	if not "exp" in tokenPayload or not checkTokenTimeValidity(tokenPayload["exp"]):
		tokenPayload = {}
	if not "jti" in tokenPayload or not validate_integer(tokenPayload["jti"]):
		tokenPayload = {}
	else:
		buyerRefreshTokenPtr = BuyerRefreshToken.objects.filter(id=int(tokenPayload["jti"]), is_active=True, buyer__blocked= False, buyer__delete_status= False)
		if not buyerRefreshTokenPtr.exists():
			tokenPayload = {}

	return tokenPayload

def  validateBuyerPasswordChangeData(buyer):

	if not "password" in buyer or buyer["password"] == None:
		return False
	if not "new_password" in buyer or  not validate_password(buyer["new_password"]):
		return False

	return True

def validateBuyerForgotPasswordData(buyer):

	if not "mobile_number" in buyer or not validate_mobile_number(buyer["mobile_number"]):
		return False
	
	return True

def validateBuyerForgotPasswordResendSMSData(buyer):
	if not "forgot_password_token" in buyer or buyer["forgot_password_token"]==None:
		return False
	return True

def validateBuyerLoginData(buyer):
	if not "mobile_number" in buyer or not  validate_mobile_number(buyer["mobile_number"]):
		return False
	if not "password" in buyer or not validate_password(buyer["password"]):
		return False
	return True

def validateBuyerForgotPasswordVerifyData(buyer):
	if not "forgot_password_token" in buyer or buyer["forgot_password_token"]==None:
		return False
	if not "otp_number" in buyer or buyer["otp_number"]==None:
		return False
	if not "new_password" in buyer or not validate_password(buyer["new_password"]):
		return False
	return True

def getBuyerForgotPasswordFromToken(forgot_password_token):

	tokenPayload = check_token_validity(forgot_password_token)

	tokenDetails = {}

	tokenDetails[0] = True
	tokenDetails[1] = customResponse(400, error_code=6, error_details=  "Invalid data for buyer forgot password sent")

	if not "sub" in tokenPayload or not tokenPayload["sub"] == "buyer forgot password":
		tokenDetails[0] = False
	if not "exp" in tokenPayload or not checkTokenTimeValidity(tokenPayload["exp"]):
		tokenDetails[0] = False
		tokenDetails[1] = customResponse(403, error_code=10, error_details=  "Token expired")
	if not "jti" in tokenPayload or not validate_integer(tokenPayload["jti"]):
		tokenDetails[0] = False
	else:
		buyerForgotPasswordTokenPtr = BuyerForgotPasswordToken.objects.filter(id=int(tokenPayload["jti"]), is_active=True)

		if len(buyerForgotPasswordTokenPtr) == 0:
			tokenDetails[0] = False	
		else:
			buyerForgotPasswordTokenPtr = buyerForgotPasswordTokenPtr[0]
			tokenDetails[1] = buyerForgotPasswordTokenPtr

	return tokenDetails