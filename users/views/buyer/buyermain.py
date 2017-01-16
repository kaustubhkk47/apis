from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string, validate_integer, validate_bool, getArrFromString
import json

from ...models.buyer import *
from catalog.models.category import Category
from catalog.models.product import Product
from address.models.state import State
from ...serializers.buyer import *
from ...models.businessType import *
from django.core.paginator import Paginator

import logging
log = logging.getLogger("django")

import time

from pandas import DataFrame

def get_buyer_details(request,parameters = {}):
	try:
		buyers = filterBuyer(parameters)

		response = {
			"buyers" : parse_buyer(buyers, parameters)
		}
		closeDBConnection()

		return customResponse(200, response)
	except Exception as e:
		log.critical(e)
		return customResponse(500)

def get_buyer_access_token_details(request,parameters = {}):
	try:
		buyerPanelURL = parameters["buyer_panel_url"].split("-")
		try:
			buyerID = int(buyerPanelURL[0])
			timeStamp = int(buyerPanelURL[1])
		except Exception as e:
			return customResponse(400, error_code=5, error_details="Invalid data in request sent")

		buyerPtr = Buyer.objects.get(id=buyerID)

		if int(time.mktime(buyerPtr.created_at.timetuple())) != timeStamp:
			closeDBConnection()
			return customResponse(400, error_code=6, error_details="Invalid time sent")

		from urlHandlers.user_handler import getBuyerToken

		response = {
			"token" : getBuyerToken(buyerPtr),
			"buyer": serialize_buyer(buyerPtr)
		}
		closeDBConnection()

		return customResponse(200, response)
	except Exception as e:
		closeDBConnection()
		log.critical(e)
		return customResponse(500)

def post_new_buyer(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer) or not validateBuyerData(buyer, Buyer(), 1):
		return customResponse(400, error_code=5, error_details=  "Invalid data for buyer sent")

	if buyer["email"] != None and buyerEmailExists(buyer["email"]):
		return customResponse(400, error_code=6, error_details=  "buyer email already exists")

	if buyerMobileNumberExists(buyer["mobile_number"]):
		return customResponse(400, error_code=6, error_details= "buyer phone number already exists")

	if not "address" in buyer or buyer["address"]==None:
		buyer["address"] = {}
		
	validateBuyerAddressData(buyer["address"], BuyerAddress())

	if not "details" in buyer or buyer["details"]==None:
		buyer["details"] = {}

	validateBuyerDetailsData(buyer["details"], BuyerDetails(), 1)

	try:
		newBuyer = Buyer()

		populateBuyer(newBuyer, buyer)
		newBuyer.password = buyer["mobile_number"]
		newBuyer.save()
		
		buyeraddress = buyer["address"]
		newAddress = BuyerAddress(buyer=newBuyer)
		populateBuyerAddress(newAddress, buyeraddress)
		newAddress.priority = 0
		if newAddress.alias == "":
			newAddress.alias = "Store"

		buyerdetails = buyer["details"]
		newBuyerDetails = BuyerDetails(buyer = newBuyer)
		if "buyertypeID" in buyer["details"] and validate_integer(buyer["details"]["buyertypeID"]):
			businessTypePtr = BusinessType.objects.filter(id=int(buyer["details"]["buyertypeID"]), can_be_buyer=True)
			if len(businessTypePtr) > 0:
				businessTypePtr = businessTypePtr[0]
				newBuyerDetails.buyer_type = businessTypePtr
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

def post_new_buyer_address(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_address = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if parameters["isBuyer"] == 1:
		buyer_address["buyerID"] = parameters["buyersArr"][0]
	elif not "buyerID" in buyer_address or not validate_integer(buyer_address["buyerID"]):
		return customResponse(400, error_code=5,  error_details= "Id for buyer not sent")

	if not len(buyer_address) or not validateBuyerAddressData(buyer_address, BuyerAddress(), 1):
		return customResponse(400, error_code=5, error_details=  "Invalid data for buyer address sent")

	try:
		addressPresent = False
		if "client_id" in buyer_address and str(buyer_address["client_id"]) != "" and len(str(buyer_address["client_id"])) > 6:
			newAddress = BuyerAddress.objects.filter(buyer_id=int(buyer_address["buyerID"]), client_id=str(buyer_address["client_id"]))
			if len(newAddress) != 0:
				addressPresent = True
				newAddress = newAddress[0]
		if not addressPresent:
			newAddress = BuyerAddress(buyer_id=int(buyer_address["buyerID"]))
		populateBuyerAddress(newAddress, buyer_address)
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
		return customResponse(200, {"address" : serialize_buyer_address(newAddress)})

def update_buyer(request, parameters = {}):
	try:
		requestbody = request.body.decode("utf-8")
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer):
		return customResponse(400, error_code=5,  error_details="Id for buyer not sent")

	if parameters["isBuyer"] == 1:
		buyer["buyerID"] = parameters["buyersArr"][0]
	elif not "buyerID" in buyer or not validate_integer(buyer["buyerID"]):
		return customResponse(400, error_code=5,  error_details="Id for buyer not sent")

	buyerPtr = Buyer.objects.filter(id=int(buyer["buyerID"]), delete_status=False).select_related('buyerdetails')

	if len(buyerPtr) == 0:
		return customResponse(400, error_code=6,  error_details= "Invalid id for buyer sent")

	buyerPtr = buyerPtr[0]

	detailsPresent = 1
	detailsSent = 0
	addressSent = 0

	if not validateBuyerData(buyer, buyerPtr, 0):
		return customResponse(400, error_code=5,  error_details="Invalid data for buyer sent")

	try:
		populateBuyer(buyerPtr, buyer)

		if "details" in buyer and buyer["details"]!=None:
			detailsSent = 1
			buyerdetails = buyer["details"]
			if hasattr(buyerPtr, "buyerdetails"):
				validateBuyerDetailsData(buyerdetails, buyerPtr.buyerdetails, 0)
				populateBuyerDetails(buyerPtr.buyerdetails, buyerdetails)
				if "buyertypeID" in buyer["details"] and validate_integer(buyer["details"]["buyertypeID"]):
					businessTypePtr = BusinessType.objects.filter(id=int(buyer["details"]["buyertypeID"]))
					if len(businessTypePtr) > 0:
						businessTypePtr = businessTypePtr[0]
						buyerPtr.buyerdetails.buyer_type = businessTypePtr
			else:
				detailsPresent = 0
				validateBuyerDetailsData(buyerdetails, BuyerDetails())
				newBuyerDetails = BuyerDetails(buyer = buyerPtr)
				if "buyertypeID" in buyer["details"] and validate_integer(buyer["details"]["buyertypeID"]):
					businessTypePtr = BusinessType.objects.filter(id=int(buyer["details"]["buyertypeID"]), can_be_buyer=True)
					if len(businessTypePtr) > 0:
						businessTypePtr = businessTypePtr[0]
						newBuyerDetails.buyer_type = businessTypePtr
				populateBuyerDetails(newBuyerDetails,buyerdetails)

		if "address" in buyer and buyer["address"]!=None:
			addressSent = 1
			buyeraddress = buyer["address"]
			if not "addressID" in buyeraddress or not buyeraddress["addressID"] or not validate_integer(buyeraddress["addressID"]):
				return customResponse(400, error_code=5,  error_details="Address id not sent")
			buyerAddressPtr = BuyerAddress.objects.filter(id = int(buyeraddress["addressID"]))

			if len(buyerAddressPtr) == 0:
				return customResponse(400, error_code=6,  error_details="Invalid address id sent")

			buyerAddressPtr = buyerAddressPtr[0]

			if(buyerAddressPtr.buyer_id != buyerPtr.id):
				return customResponse(400, error_code=6,  error_details= "Address id for incorrect buyer sent")
				
			validateBuyerAddressData(buyeraddress, buyerAddressPtr)
			populateBuyerAddress(buyerAddressPtr, buyeraddress)


		buyerPtr.save()
		if detailsSent == 1 and detailsPresent == 1:
			buyerPtr.buyerdetails.save()
		if detailsPresent == 0:
			newBuyerDetails.save()
		if addressSent == 1:
			buyerAddressPtr.save()
			newBuyerAddressHistory = BuyerAddressHistory()
			newBuyerAddressHistory.populateFromBuyerAddress(buyerAddressPtr)
			newBuyerAddressHistory.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer": serialize_buyer(buyerPtr, parameters)})

def update_buyer_address(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_address = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if parameters["isBuyer"] == 1:
		buyer_address["buyerID"] = parameters["buyersArr"][0]
	elif not "buyerID" in buyer_address or not validate_integer(buyer_address["buyerID"]):
		return customResponse(400, error_code=5,  error_details= "Id for buyer not sent")

	if not len(buyer_address):
		return customResponse(400, error_code=5, error_details=  "Invalid data for buyer address sent")

	if not "addressID" in buyer_address or not validate_integer(buyer_address["addressID"]):
		return customResponse(400, error_code=5, error_details=  "Address Id for buyer not sent")

	buyerAddressPtr = BuyerAddress.objects.filter(buyer_id=int(buyer_address["buyerID"]), id =int(buyer_address["addressID"]))

	if len(buyerAddressPtr) == 0:
		return customResponse(400, error_code=6, error_details=  "Invalid Address Id for buyer sent")

	buyerAddressPtr = buyerAddressPtr[0]

	validateBuyerAddressData(buyer_address, BuyerAddress(), 0)

	try:
		
		populateBuyerAddress(buyerAddressPtr, buyer_address)
		buyerAddressPtr.save()

		newBuyerAddressHistory = BuyerAddressHistory()
		newBuyerAddressHistory.populateFromBuyerAddress(buyerAddressPtr)
		newBuyerAddressHistory.save()
		 
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"address" : serialize_buyer_address(buyerAddressPtr)})

def delete_buyer(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer) or not "buyerID" in buyer or not buyer["buyerID"] or not validate_integer(buyer["buyerID"]):
		return customResponse(400, error_code=5,  error_details= "Id for buyer not sent")

	buyerPtr = Buyer.objects.filter(id=int(buyer["buyerID"]), delete_status=False)

	if len(buyerPtr) == 0:
		return customResponse(400, error_code=6,  error_details="Invalid id for buyer sent")

	buyerPtr = buyerPtr[0]

	try:
		buyerPtr.delete_status = True
		buyerPtr.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer": "buyer deleted"})