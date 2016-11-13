from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string, validate_integer, validate_bool, getArrFromString
import json

from ...models.buyer import *
from ...serializers.buyer import *
import logging
log = logging.getLogger("django")

def post_new_buyer_registration(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_registration = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_registration) or not validateBuyerRegistrationData(buyer_registration):
		return customResponse(400, error_code=5, error_details=  "Invalid data for buyer registration sent")

	if buyerEmailExists(buyer_registration["email"]):
		return customResponse(400, error_code=6, error_details=  "buyer email already exists")

	if buyerMobileNumberExists(buyer_registration["mobile_number"]):
		return customResponse(400, error_code=6, error_details= "buyer phone number already exists")

	## Invalidate all registrations with same email or mobile number

	BuyerRegistration.objects.filter(email=buyer_registration["email"]).update(is_active=False)
	BuyerRegistration.objects.filter(mobile_number=buyer_registration["mobile_number"]).update(is_active=False)

	try:
		newBuyerRegistration = BuyerRegistration()
		newBuyerRegistration.populateBuyerRegistration(buyer_registration)
		newBuyerRegistration.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		## Send mobile number verification SMS

		newBuyerRegistration.sendVerificationSMS()

		closeDBConnection()
		return customResponse(200, {"buyer_registration" : serialize_buyer_registration(newBuyerRegistration, parameters)})

def post_buyer_registration_resend_sms(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_registration = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_registration) or not validateBuyerRegistrationResendSMSData(buyer_registration):
		return customResponse(400, error_code=5, error_details=  "Invalid data for buyer registration sent")

	tokenDetails = getBuyerRegistrationFromToken(buyer_registration["registration_token"])

	if tokenDetails[0] == False:
		return tokenDetails[1]

	buyerRegistrationPtr = tokenDetails[1]

	if buyerRegistrationPtr.messages_sent > 3:
		return customResponse(400, error_code=11, error_details=  "SMS count exceeded")

	try:
		buyerRegistrationPtr.sendVerificationSMS()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"success" : "sms sent"})

def post_buyer_registration_verify(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_registration = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_registration) or not validateBuyerRegistrationVerifyData(buyer_registration):
		return customResponse(400, error_code=5, error_details=  "Invalid data for buyer registration sent")

	tokenDetails = getBuyerRegistrationFromToken(buyer_registration["registration_token"])

	if tokenDetails[0] == False:
		return tokenDetails[1]

	buyerRegistrationPtr = tokenDetails[1]

	if not buyer_registration["otp_number"] == buyerRegistrationPtr.otp_number:
		buyerRegistrationPtr.verification_attempts += 1
		if buyerRegistrationPtr.verification_attempts >4:
			buyerRegistrationPtr.is_active = 0
		buyerRegistrationPtr.save()
		return customResponse(400, error_code=6, error_details=  "Wrong OTP sent")

	buyer = {}

	buyerRegistrationPtr.fillBuyerData(buyer)

	buyer["address"] = {}
	validateBuyerAddressData(buyer["address"], BuyerAddress())

	buyer["details"] = {}
	validateBuyerDetailsData(buyer["details"], BuyerDetails(), 1)

	validateBuyerData(buyer, Buyer(), 1)

	try:
		buyerRegistrationPtr.is_active = False
		buyerRegistrationPtr.save()

		newBuyer = Buyer()

		populateBuyer(newBuyer, buyer)
		newBuyer.save()
		
		buyeraddress = buyer["address"]
		newAddress = BuyerAddress(buyer=newBuyer)
		populateBuyerAddress(newAddress, buyeraddress)

		buyerdetails = buyer["details"]
		newBuyerDetails = BuyerDetails(buyer = newBuyer)
		populateBuyerDetails(newBuyerDetails, buyerdetails)
		
		newBuyerDetails.save()
		newAddress.save()

		newBuyerAddressHistory = BuyerAddressHistory()
		newBuyerAddressHistory.populateFromBuyerAddress(newAddress)
		newBuyerAddressHistory.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer" : serialize_buyer(newBuyer)})