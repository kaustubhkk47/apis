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

def get_buyer_purchasing_state_details(request,parameters = {}):
	try:
		buyersPurchasingState = filterBuyerPurchasingState(parameters)

		response = {
			"buyer_purchasing_states" : parse_buyer_purchasing_state(buyersPurchasingState, parameters)
		}
		closeDBConnection()

		return customResponse(200, response)
	except Exception as e:
		log.critical(e)
		return customResponse(500)

def get_buyer_buys_from_details(request,parameters = {}):
	try:
		buyerBuysFrom = filterBuyerBuysFrom(parameters)

		response = {
			"buyer_buys_from" : parse_buyer_buys_from(buyerBuysFrom, parameters)
		}
		closeDBConnection()

		return customResponse(200, response)
	except Exception as e:
		log.critical(e)
		return customResponse(500)

def post_new_buyer_purchasing_state(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_purchasing_state = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_purchasing_state) or not "buyerID" in buyer_purchasing_state or not validate_integer(buyer_purchasing_state["buyerID"]):
		return customResponse(400, error_code=5, error_details=  "Id for buyer not sent")

	buyerPtr = Buyer.objects.filter(id=int(buyer_purchasing_state["buyerID"]), delete_status=False)

	if not buyerPtr.exists():
		return customResponse(400, error_code=6, error_details= "Invalid id for buyer sent")

	if not "stateID" in buyer_purchasing_state or not validate_integer(buyer_purchasing_state["stateID"]):
		return customResponse(400, error_code=5, error_details= "Id for state not sent")

	statePtr = State.objects.filter(id=int(buyer_purchasing_state["stateID"]))

	if not statePtr.exists():
		return customResponse(400, error_code=6, error_details= "Invalid id for state sent")

	BuyerPurchasingStatePtr = BuyerPurchasingState.objects.filter(buyer_id=int(buyer_purchasing_state["buyerID"]),state_id=int(buyer_purchasing_state["stateID"]))

	if len(BuyerPurchasingStatePtr)>0:
		BuyerPurchasingStatePtr = BuyerPurchasingStatePtr[0]
		if BuyerPurchasingStatePtr.delete_status == True:
			BuyerPurchasingStatePtr.delete_status = False
			BuyerPurchasingStatePtr.save()
			closeDBConnection()
			return customResponse(200, {"buyer_purchasing_state" : serialize_buyer_purchasing_state(BuyerPurchasingStatePtr)})
		else:
			return customResponse(400, error_code=6, error_details=  "Buyer purchasing_state already exists")

	try:
		newBuyerPurchasingState = BuyerPurchasingState(buyer_id=int(buyer_purchasing_state["buyerID"]),state_id=int(buyer_purchasing_state["stateID"]))
		newBuyerPurchasingState.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer_purchasing_state" : serialize_buyer_purchasing_state(newBuyerPurchasingState)})

def post_new_buyer_buys_from(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_buys_from = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_buys_from) or not "buyerID" in buyer_buys_from or not validate_integer(buyer_buys_from["buyerID"]):
		return customResponse(400, error_code=5, error_details= "Id for buyer not sent")

	buyerPtr = Buyer.objects.filter(id=int(buyer_buys_from["buyerID"]), delete_status=False)

	if not buyerPtr.exists():
		return customResponse(400, error_code=6, error_details= "Invalid id for buyer sent")

	if not "businesstypeID" in buyer_buys_from or not validate_integer(buyer_buys_from["businesstypeID"]):
		return customResponse(400, error_code=5, error_details= "Id for state not sent")

	businessTypePtr = BusinessType.objects.filter(id=int(buyer_buys_from["businesstypeID"]), can_buyer_buy_from=True)

	if not businessTypePtr.exists():
		return customResponse(400, error_code=6, error_details= "Invalid id for business type sent")

	BuyerBuysFromPtr = BuyerBuysFrom.objects.filter(buyer_id=int(buyer_buys_from["buyerID"]),business_type_id=int(buyer_buys_from["businesstypeID"]))

	if len(BuyerBuysFromPtr)>0:
		BuyerBuysFromPtr = BuyerBuysFromPtr[0]
		if BuyerBuysFromPtr.delete_status == True:
			BuyerBuysFromPtr.delete_status = False
			BuyerBuysFromPtr.save()
			closeDBConnection()
			return customResponse(200, {"buyer_buys_from" : serialize_buyer_buys_from(BuyerBuysFromPtr)})
		else:
			return customResponse(400, error_code=6, error_details= "Buyer buys_from already exists")

	try:
		newBuyerBuysFrom = BuyerBuysFrom(buyer_id=int(buyer_buys_from["buyerID"]),business_type_id=int(buyer_buys_from["businesstypeID"]))
		newBuyerBuysFrom.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer_buys_from" : serialize_buyer_buys_from(newBuyerBuysFrom)})

def post_new_buyer_panel_tracking(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	#if not len(buyer) or not "buyerID" in buyer or not validate_integer(buyer["buyerID"]):
	#	return customResponse("4XX", {"error": "Id for buyer not sent"})

	buyer["buyerID"] = parameters["buyersArr"][0]

	buyerPtr = Buyer.objects.filter(id=int(buyer["buyerID"]), delete_status=False)

	if not buyerPtr.exists():
		return customResponse(400, error_code=6, error_details= "Invalid id for buyer sent")

	if not "page_closed" in buyer or buyer["page_closed"] ==None:
		return customResponse(400, error_code=6, error_details= "Page number not sent")
	try:
		newBuyerPanelInstructionsTracking = BuyerPanelInstructionsTracking(buyer_id=int(buyer["buyerID"]), page_closed=buyer["page_closed"])
		newBuyerPanelInstructionsTracking.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer_product_tracking":"successfully added"})

def delete_buyer_purchasing_state(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_purchasing_state = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_purchasing_state) or not "buyerpurchasingstateID" in buyer_purchasing_state or not validate_integer(buyer_purchasing_state["buyerpurchasingstateID"]):
		return customResponse(400, error_code=5,  error_details= "Id for buyer purchasing_state not sent")

	buyerPurchasingStatePtr = BuyerPurchasingState.objects.filter(id=int(buyer_purchasing_state["buyerpurchasingstateID"]))

	if len(buyerPurchasingStatePtr) == 0:
		return customResponse(400, error_code=6,  error_details= "Invalid id for buyer purchasing_state sent")

	try:
		buyerPurchasingStatePtr.update(delete_status = True)
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer": "buyer purchasing_state deleted"})

def delete_buyer_buys_from(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_buys_from = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_buys_from) or not "buyerbuysfromID" in buyer_buys_from or not validate_integer(buyer_buys_from["buyerbuysfromID"]):
		return customResponse(400, error_code=5,  error_details="Id for buyer buys_from not sent")

	buyerBuysFromPtr = BuyerBuysFrom.objects.filter(id=int(buyer_buys_from["buyerbuysfromID"]))

	if len(buyerBuysFromPtr) == 0:
		return customResponse(400, error_code=6,  error_details="Invalid id for buyer buys_from sent")

	try:
		buyerBuysFromPtr.update(delete_status = True)
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer": "buyer buys_from deleted"})