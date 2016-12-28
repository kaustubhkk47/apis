from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string, validate_integer, validate_bool, getArrFromString
import json

from ...models.buyer import *
from ...serializers.buyer import *
import logging
log = logging.getLogger("django")

from django.utils import timezone

def post_buyer_login(request, parameters):

	try:
		requestbody = request.body.decode("utf-8")
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer) or not validateBuyerLoginData(buyer):
		return customResponse(400, error_code=5, error_details=  "Invalid data sent in request")

	#mobile_number = request.POST.get('mobile_number', '')
	#password = request.POST.get('password', '')

	mobile_number = buyer["mobile_number"]
	password = buyer["password"]

	## Instead take mobile number and password from request body

	if not mobile_number or not password:
		return customResponse(400, error_code=5, error_details= "Either mobile number or password was empty")

	# if check_token(request)
	try:
		buyerPtr = Buyer.objects.get(mobile_number=mobile_number,delete_status=False, blocked = False)
	except Buyer.DoesNotExist:
		return customResponse(403, error_code=7, error_details="Invalid mobile number")

	if not buyerPtr.password == password:
		return customResponse(401, error_code=9, error_details="Invalid buyer credentials")

	try:
		newBuyerRefreshToken = BuyerRefreshToken()
		newBuyerRefreshToken.populateFromBuyer(buyerPtr)
		newBuyerRefreshToken.save()

		newBuyerAccessToken = BuyerAccessToken()
		newBuyerAccessToken.populateFromRefreshToken(newBuyerRefreshToken)
		newBuyerAccessToken.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		response_body = {}
		response_body["access_token"] = serialize_buyer_access_token(newBuyerAccessToken, parameters)
		response_body["refresh_token"] = serialize_buyer_refresh_token(newBuyerRefreshToken, parameters)
		response_body["buyer"] = serialize_buyer(buyerPtr, parameters)

		closeDBConnection()
		return customResponse(200, {"buyer_login" : response_body})

def get_buyer_renew_access_token(request, parameters):

	refresh_token = getAccessToken(request, "refresh_token")

	if refresh_token == "":
		return customResponse(400, error_code=5, error_details= "Refresh token not sent")

	tokenPayload = validateBuyerRefreshToken(refresh_token)

	if tokenPayload == {}:
		return customResponse(403, error_code=7, error_details=  "Token invalid")

	buyerRefreshTokenPtr = BuyerRefreshToken.objects.filter(id=int(tokenPayload["jti"]))
	buyerRefreshTokenPtr = buyerRefreshTokenPtr[0]

	try:
		newBuyerAccessToken = BuyerAccessToken()
		newBuyerAccessToken.populateFromRefreshToken(buyerRefreshTokenPtr)
		newBuyerAccessToken.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		response_body = {}
		response_body["access_token"] = serialize_buyer_access_token(newBuyerAccessToken, parameters)

		closeDBConnection()
		return customResponse(200, {"buyer_login" : response_body})

def post_buyer_logout(request, parameters):

	access_token = getAccessToken(request, "access_token")

	tokenPayload = validateBuyerAccessToken(access_token)

	refreshTokenID = None

	if not tokenPayload == {}:
		buyerAccessTokenPtr = BuyerAccessToken.objects.filter(id=int(tokenPayload["jti"]))

		if not len(buyerAccessTokenPtr) == 0:
			buyerAccessTokenPtr = buyerAccessTokenPtr[0]
			refreshTokenID = buyerAccessTokenPtr.buyer_refresh_token_id

	if refreshTokenID == None:
		refresh_token = getAccessToken(request, "refresh_token")
		tokenPayload = validateBuyerRefreshToken(refresh_token)

		if not tokenPayload == {}:
			refreshTokenID = int(tokenPayload["jti"])
		else:
			return customResponse(400, error_code=5, error_details= "token not sent")

	if refreshTokenID == None:
		return customResponse(403, error_code=7, error_details=  "Token invalid")

	buyerRefreshTokenPtr = BuyerRefreshToken.objects.filter(id=refreshTokenID)
	buyerRefreshTokenPtr = buyerRefreshTokenPtr[0]

	try:
		buyerRefreshTokenPtr.is_active = False
		buyerRefreshTokenPtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"success" : "successfully logged out"})

def post_buyer_change_password(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer) or not validateBuyerPasswordChangeData(buyer):
		return customResponse(400, error_code=5, error_details=  "Invalid data sent in request")

	refresh_token = getAccessToken(request, "refresh_token")

	if refresh_token == "":
		return customResponse(400, error_code=5, error_details= "Refresh token not sent")

	tokenPayload = validateBuyerRefreshToken(refresh_token)

	if tokenPayload == {}:
		return customResponse(403, error_code=7, error_details=  "Token invalid")

	buyerPtr = Buyer.objects.filter(id=parameters["buyersArr"][0], delete_status=False, blocked=False)

	if len(buyerPtr) == 0:
		return customResponse(400, error_code=6, error_details=  "Invalid buyer id sent")

	buyerPtr = buyerPtr[0]

	if not buyerPtr.password == buyer["password"]:
		return customResponse(400, error_code=9, error_details=  "Incorrect password sent")

	try:
		buyerPtr.password = buyer["new_password"]
		buyerPtr.save()
		BuyerRefreshToken.objects.filter(buyer_id=buyerPtr.id).update(is_active=False, updated_at = timezone.now())

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"success" : "successfully changed password"})

def post_buyer_forgot_password(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer) or not validateBuyerForgotPasswordData(buyer):
		return customResponse(400, error_code=5, error_details=  "Invalid data sent in request")

	buyerPtr = Buyer.objects.filter(mobile_number=buyer["mobile_number"], blocked=False, delete_status=False)

	if len(buyerPtr) == 0:
		return customResponse(400, error_code=6, error_details=  "Invalid mobile number sent")

	buyerPtr = buyerPtr[0]
	## Invalidate all registrations with same email or mobile number
	BuyerForgotPasswordToken.objects.filter(mobile_number=buyer["mobile_number"]).update(is_active=False,  updated_at = timezone.now())

	try:
		newBuyerForgotPasswordToken = BuyerForgotPasswordToken()
		newBuyerForgotPasswordToken.populateBuyerBuyerForgotPasswordToken(buyer)
		newBuyerForgotPasswordToken.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		## Send mobile number verification SMS

		newBuyerForgotPasswordToken.sendVerificationSMS()

		closeDBConnection()
		return customResponse(200, {"buyer_registration" : serialize_buyer_forgot_password_token(newBuyerForgotPasswordToken, parameters)})

def post_buyer_forgot_password_resend_sms(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer) or not validateBuyerForgotPasswordResendSMSData(buyer):
		return customResponse(400, error_code=5, error_details=  "Invalid data for buyer forgot password sent")

	tokenDetails = getBuyerForgotPasswordFromToken(buyer["forgot_password_token"])

	if tokenDetails[0] == False:
		return tokenDetails[1]

	buyerForgotPasswordTokenPtr = tokenDetails[1]

	if buyerForgotPasswordTokenPtr.messages_sent > 3:
		return customResponse(400, error_code=11, error_details=  "SMS count exceeded")

	try:
		buyerForgotPasswordTokenPtr.sendVerificationSMS()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"success" : "sms sent"})

def post_buyer_forgot_password_verify(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer) or not validateBuyerForgotPasswordVerifyData(buyer):
		return customResponse(400, error_code=5, error_details=  "Invalid data for buyer forgot password sent")

	tokenDetails = getBuyerForgotPasswordFromToken(buyer["forgot_password_token"])

	if tokenDetails[0] == False:
		return tokenDetails[1]

	buyerForgotPasswordTokenPtr = tokenDetails[1]

	if not buyer["otp_number"] == buyerForgotPasswordTokenPtr.otp_number:
		buyerForgotPasswordTokenPtr.verification_attempts += 1
		if buyerForgotPasswordTokenPtr.verification_attempts >4:
			buyerForgotPasswordTokenPtr.is_active = 0
		buyerForgotPasswordTokenPtr.save()
		return customResponse(400, error_code=6, error_details=  "Wrong OTP sent")

	buyerPtr = Buyer.objects.filter(mobile_number=buyerForgotPasswordTokenPtr.mobile_number, blocked=False, delete_status=False)

	if len(buyerPtr) == 0:
		return customResponse(400, error_code=5, error_details=  "Invalid data for buyer registration sent")

	buyerPtr = buyerPtr[0]

	try:
		buyerForgotPasswordTokenPtr.is_active = False
		buyerForgotPasswordTokenPtr.save()

		buyerPtr.password = buyer["new_password"]
		buyerPtr.save()
		BuyerForgotPasswordToken.objects.filter(mobile_number=buyerForgotPasswordTokenPtr.mobile_number).update(is_active=False,  updated_at = timezone.now())

		newBuyerRefreshToken = BuyerRefreshToken()
		newBuyerRefreshToken.populateFromBuyer(buyerPtr)
		newBuyerRefreshToken.save()

		newBuyerAccessToken = BuyerAccessToken()
		newBuyerAccessToken.populateFromRefreshToken(newBuyerRefreshToken)
		newBuyerAccessToken.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		
		response_body = {}
		response_body["access_token"] = serialize_buyer_access_token(newBuyerAccessToken, parameters)
		response_body["refresh_token"] = serialize_buyer_refresh_token(newBuyerRefreshToken, parameters)
		response_body["buyer"] = serialize_buyer(buyerPtr, parameters)

		return customResponse(200, response_body)

def put_buyer_firebase_token_details(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer) or not BuyerFireBaseToken.validateBuyerFireBaseTokenData(buyer):
		return customResponse(400, error_code=5,  error_details= "Invalid data sent in request")
	try:
		buyerID = parameters["buyersArr"][0]
	except Exception as e:
		buyerID = None

	try:

		buyerFireBaseTokenPtr, created = BuyerFireBaseToken.objects.get_or_create( instance_id = buyer["instance_id"])
		buyerFireBaseTokenPtr.buyer_id = buyerID
		buyerFireBaseTokenPtr.token = buyer["token"]
		buyerFireBaseTokenPtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		#buyerFireBaseTokenPtr.sendWelcomeNotification()
		return customResponse(200, {"token":"token successfully created"})