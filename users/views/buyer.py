from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string, validate_integer, validate_bool
import json

from ..models.buyer import *
from ..serializers.buyer import serialize_buyer, parse_buyer

import logging
log = logging.getLogger("django")

def get_buyer_details(request,buyerParameters):
	try:
		buyers = filterBuyer(buyerParameters)

		response = {
			"buyers" : parse_buyer(buyers)
		}
		closeDBConnection()

		return customResponse("2XX", response)
	except Exception as e:
		log.critical(e)
		return customResponse("4XX", {"error": "Invalid request"})

def post_new_buyer(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer) or not validateBuyerData(buyer, Buyer(), 1):
		return customResponse("4XX", {"error": "Invalid data for buyer sent"})

	if buyerEmailExists(buyer["email"]):
		return customResponse("4XX", {"error": "buyer email already exists"})

	if buyerMobileNumberExists(buyer["mobile_number"]):
		return customResponse("4XX", {"error": "buyer phone number already exists"})

	if not "address" in buyer or buyer["address"]==None:
		buyer["address"] = {}
		
	validateBuyerAddressData(buyer["address"], BuyerAddress())

	if not "details" in buyer or buyer["details"]==None:
		buyer["details"] = {}

	try:

		validateBuyerDetailsData(buyer["details"], BuyerDetails())

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
		 
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer" : serialize_buyer(newBuyer)})

def update_buyer(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer) or not "buyerID" in buyer or buyer["buyerID"]==None or not validate_integer(buyer["buyerID"]):
		return customResponse("4XX", {"error": "Id for buyer not sent"})

	buyerPtr = Buyer.objects.filter(id=int(buyer["buyerID"])).select_related('buyerdetails')

	if len(buyerPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for buyer sent"})

	buyerPtr = buyerPtr[0]

	detailsPresent = 1
	detailsSent = 0
	addressSent = 0

	if not validateBuyerData(buyer, buyerPtr, 0):
		return customResponse("4XX", {"error": "Invalid data for buyer sent"})

	try:
		populateBuyer(buyerPtr, buyer)

		if "details" in buyer and buyer["details"]!=None:
			detailsSent = 1
			buyerdetails = buyer["details"]
			if hasattr(buyerPtr, "buyerdetails"):
				validateBuyerDetailsData(buyerdetails, buyerPtr.buyerdetails)
				populateBuyerDetails(buyerPtr.buyerdetails, buyerdetails)	
			else:
				detailsPresent = 0
				validateBuyerDetailsData(buyerdetails, BuyerDetails())
				newBuyerDetails = BuyerDetails(buyer = buyerPtr)
				populateBuyerDetails(newBuyerDetails,buyerdetails)

		if "address" in buyer and buyer["address"]!=None:
			addressSent = 1
			buyeraddress = buyer["address"]
			if not "addressID" in buyeraddress or not buyeraddress["addressID"] or not validate_integer(buyeraddress["addressID"]):
				return customResponse("4XX", {"error": "Address id not sent"})
			buyerAddressPtr = BuyerAddress.objects.filter(id = int(buyeraddress["addressID"]))

			if len(buyerAddressPtr) == 0:
				return customResponse("4XX", {"error": "Invalid address id sent"})

			buyerAddressPtr = buyerAddressPtr[0]
			validateBuyerAddressData(buyeraddress, buyerAddressPtr)
			populateBuyerAddress(buyerAddressPtr, buyeraddress)


		buyerPtr.save()
		if detailsSent == 1 and detailsPresent == 1:
			buyerPtr.buyerdetails.save()
		if detailsPresent == 0:
			newBuyerDetails.save()
		if addressSent == 1:
			buyerAddressPtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "could not update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer": serialize_buyer(buyerPtr)})

def delete_buyer(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer) or not "buyerID" in buyer or not buyer["buyerID"] or not validate_integer(buyer["buyerID"]):
		return customResponse("4XX", {"error": "Id for buyer not sent"})

	buyerPtr = Buyer.objects.filter(id=int(buyer["buyerID"]))

	if len(buyerPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for buyer sent"})

	buyerPtr = buyerPtr[0]

	try:
		buyerPtr.delete_status = True
		buyerPtr.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "could not delete"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer": "buyer deleted"})
