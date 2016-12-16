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

def get_buyer_store_lead_details(request,parameters = {}):
	try:
		buyerStoreLeads = filterBuyerStoreLeads(parameters)

		paginator = Paginator(buyerStoreLeads, parameters["itemsPerPage"])

		try:
			pageItems = paginator.page(parameters["pageNumber"])
		except Exception as e:
			pageItems = []

		response = {
			"buyer_store_leads" : parse_buyer_store_lead(buyerStoreLeads, parameters)
		}

		responsePaginationParameters(response, paginator, parameters)
		closeDBConnection()

		return customResponse(200, response)
	except Exception as e:
		log.critical(e)
		return customResponse(500)

def post_new_buyer_store_lead(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_store_lead = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_store_lead):
		return customResponse(400, error_code=5, error_details= "Id for buyer not sent")

	if parameters["isBuyer"] == 1 or parameters["isBuyerStore"] == 1:
		buyer_store_lead["buyerID"] = parameters["buyersArr"][0]
	elif not "buyerID" in buyer_store_lead  or not validate_integer(buyer_store_lead["buyerID"]):
		return customResponse(400, error_code=5, error_details= "Id for buyer not sent")

	buyerPtr = Buyer.objects.filter(id=int(buyer_store_lead["buyerID"]), delete_status=False)

	if not buyerPtr.exists():
		return customResponse(400, error_code=6, error_details= "Invalid id for buyer sent")


	if not "productID" in buyer_store_lead or not validate_integer(buyer_store_lead["productID"]):
		return customResponse(400, error_code=5, error_details= "Id for product not sent")

	productParameters = {}
	productParameters["productsArr"] = [int(buyer_store_lead["productID"])]
	productParameters["product_verification"] = True
	productParameters["product_show_online"] = True
	productParameters["seller_show_online"] = True
	productParameters["category_show_online"] = True

	productPtr = filterProducts(productParameters)

	if not productPtr.exists():
		return customResponse(400, error_code=6, error_details= "Invalid id for product sent")

	newBuyerStoreLead = BuyerStoreLead(buyer_id=int(buyer_store_lead["buyerID"]), product_id = int(buyer_store_lead["productID"]))

	if not newBuyerStoreLead.validateBuyerStoreLeadData(buyer_store_lead, 1):
		return customResponse(400, error_code=5, error_details= "Invalid data for buyer store lead sent")

	try:
		newBuyerStoreLead.populateBuyerStoreLead(buyer_store_lead)
		newBuyerStoreLead.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		newBuyerStoreLead.sendRetailerMail(parameters)
		newBuyerStoreLead.sendCustomerMail(parameters)
		closeDBConnection()
		return customResponse(200, {"buyer_store_lead":serialize_buyer_store_lead(newBuyerStoreLead)})


def update_buyer_store_lead(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_store_lead = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_store_lead):
		return customResponse(400, error_code=5, error_details= "Invalid data sent in request")

	if parameters["isBuyer"] == 1:
		buyer_store_lead["buyerID"] = parameters["buyersArr"][0]
	elif not "buyerID" in buyer_store_lead  or not validate_integer(buyer_store_lead["buyerID"]):
		return customResponse(400, error_code=5, error_details= "Id for buyer not sent")

	buyerPtr = Buyer.objects.filter(id=int(buyer_store_lead["buyerID"]), delete_status=False)

	if not buyerPtr.exists():
		return customResponse(400, error_code=6, error_details= "Invalid id for buyer sent")

	if not "buyerstoreleadID" in buyer_store_lead or not validate_integer(buyer_store_lead["buyerstoreleadID"]):
		return customResponse(400, error_code=5, error_details= "Id for buyer store lead not sent")

	buyerStoreLeadPtr = BuyerStoreLead.objects.filter(id=int(buyer_store_lead["buyerstoreleadID"]), buyer_id=int(buyer_store_lead["buyerID"]))

	if len(buyerStoreLeadPtr) == 0:
		return customResponse(400, error_code=6, error_details= "Invalid id for buyer store lead sent")

	
	buyerStoreLeadPtr = buyerStoreLeadPtr[0]

	if not buyerStoreLeadPtr.validateBuyerStoreLeadData(buyer_store_lead, 0):
		return customResponse(400, error_code=5, error_details=  "Invalid data for buyer store lead sent")

	try:
		buyerStoreLeadPtr.populateBuyerStoreLead(buyer_store_lead)
		buyerStoreLeadPtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer_store_lead":serialize_buyer_store_lead(buyerStoreLeadPtr)})
