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

def get_buyer_interest_details(request,parameters = {}):
	try:
		buyerInterests = filterBuyerInterest(parameters)

		response = {
			"buyer_interests" : parse_buyer_interest(buyerInterests, parameters)
		}
		closeDBConnection()

		return customResponse(200, response)
	except Exception as e:
		log.critical(e)
		return customResponse(500)

def post_new_buyer_interest(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_interest = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_interest):
		return customResponse(400, error_code=5, error_details=  "Id for buyer not sent")

	if parameters["isBuyer"] == 1:
		buyer_interest["buyerID"] = parameters["buyersArr"][0]
	elif not "buyerID" in buyer_interest  or not validate_integer(buyer_interest["buyerID"]):
		return customResponse(400, error_code=5, error_details= "Id for buyer not sent")

	buyerPtr = Buyer.objects.filter(id=int(buyer_interest["buyerID"]), delete_status=False)

	if not  buyerPtr.exists():
		return customResponse(400, error_code=6, error_details= "Invalid id for buyer sent")


	if not "categoryID" in buyer_interest or not validate_integer(buyer_interest["categoryID"]):
		return customResponse(400, error_code=5, error_details=  "Id for category not sent")

	categoryPtr = Category.objects.filter(id=int(buyer_interest["categoryID"]))

	if not categoryPtr.exists():
		return customResponse(400, error_code=6, error_details= "Invalid id for category sent")

	BuyerInterestPtr = BuyerInterest.objects.filter(buyer_id=int(buyer_interest["buyerID"]),category_id=int(buyer_interest["categoryID"]))

	if BuyerInterestPtr.exists():
		return customResponse(400, error_code=6, error_details= "Buyer interest for category already exists")

	if not validateBuyerInterestData(buyer_interest, BuyerInterest(), 1):
		return customResponse(400, error_code=5, error_details= "Invalid data for buyer interest sent")

	try:
		newBuyerInterest = BuyerInterest(buyer_id=int(buyer_interest["buyerID"]),category_id = int(buyer_interest["categoryID"]))
		populateBuyerInterest(newBuyerInterest, buyer_interest)
		newBuyerInterest.save()

		newBuyerInterestHistory = BuyerInterestHistory(buyer_interest=newBuyerInterest)
		populateBuyerInterest(newBuyerInterestHistory, buyer_interest)
		newBuyerInterestHistory.save()

		productPtr = filterBuyerInterestProducts(newBuyerInterest)

		buyerProductPtr = BuyerProducts.objects.filter(buyer_id = int(buyer_interest["buyerID"]))

		intersectingProducts = getIntersectingProducts(productPtr, buyerProductPtr)

		buyerProductsToCreate = []

		for product_id in intersectingProducts[0]:
			buyerProduct = BuyerProducts(buyer_id=int(buyer_interest["buyerID"]), product_id=product_id, buyer_interest=newBuyerInterest)
			buyerProductsToCreate.append(buyerProduct)

		BuyerProducts.objects.bulk_create(buyerProductsToCreate)

		BuyerProducts.objects.filter(id__in=intersectingProducts[1]).update(buyer_interest=newBuyerInterest,delete_status=False)

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer_interest" : serialize_buyer_interest(newBuyerInterest)})

def update_buyer_interest(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_interest = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_interest) or not "buyerinterestID" in buyer_interest or not validate_integer(buyer_interest["buyerinterestID"]):
		return customResponse(400, error_code=5,  error_details= "Id for buyer interest not sent")

	buyerInterestPtr = BuyerInterest.objects.filter(id=int(buyer_interest["buyerinterestID"]))

	if len(buyerInterestPtr) == 0:
		return customResponse(400, error_code=6,  error_details= "Invalid id interest for buyer sent")

	buyerInterestPtr = buyerInterestPtr[0]

	if parameters["isBuyer"] == 1 and not buyerInterestPtr.buyer_id == parameters["buyersArr"][0]:
		return customResponse(400, error_code=6,  error_details= "Interest id for wrong buyer sent")

	if not validateBuyerInterestData(buyer_interest, buyerInterestPtr, 0):
		return customResponse(400, error_code=5,  error_details= "Invalid data for buyer interest sent")

	buyerProductPtr = BuyerProducts.objects.filter(buyer_interest_id = buyerInterestPtr.id)

	forceEvaluation = len(buyerProductPtr)

	buyerAllProductPtr = BuyerProducts.objects.filter(buyer_id = buyerInterestPtr.buyer_id)

	forceEvaluation = len(buyerAllProductPtr)

	try:
		
		populateBuyerInterest(buyerInterestPtr, buyer_interest)
		buyerInterestPtr.save()

		newBuyerInterestHistory = BuyerInterestHistory(buyer_interest=buyerInterestPtr)
		populateBuyerInterest(newBuyerInterestHistory, buyer_interest)
		newBuyerInterestHistory.save()

		productPtr = filterBuyerInterestProducts(buyerInterestPtr)

		intersectingProducts = getIntersectingProducts(productPtr, buyerProductPtr)

		intersectingProductsAll = getIntersectingProducts(productPtr, buyerAllProductPtr)

		buyerProductsToCreate = []

		for product_id in intersectingProductsAll[0]:
			buyerProduct = BuyerProducts(buyer_id=buyerInterestPtr.buyer_id, product_id=product_id, buyer_interest=buyerInterestPtr)
			buyerProductsToCreate.append(buyerProduct)

		BuyerProducts.objects.bulk_create(buyerProductsToCreate)

		BuyerProducts.objects.filter(id__in=intersectingProducts[1]).update(buyer_interest=buyerInterestPtr,delete_status=False)

		BuyerProducts.objects.filter(id__in=intersectingProducts[2],responded=0).update(delete_status=True, buyer_interest_id=None)

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer" : serialize_buyer_interest(buyerInterestPtr)})

def delete_buyer_interest(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_interest = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_interest) or not "buyerinterestID" in buyer_interest or not validate_integer(buyer_interest["buyerinterestID"]):
		return customResponse(400, error_code=5,  error_details=  "Id for buyer interest not sent")

	buyerInterestPtr = BuyerInterest.objects.filter(id=int(buyer_interest["buyerinterestID"]))

	if len(buyerInterestPtr) == 0:
		return customResponse(400, error_code=6,  error_details= "Invalid id for buyer interest sent")

	buyerInterestPtr = buyerInterestPtr[0]

	if parameters["isBuyer"] == 1 and not buyerInterestPtr.buyer_id == parameters["buyersArr"][0]:
		return customResponse(400, error_code=6,  error_details= "Interest id for wrong buyer sent")

	try:
		buyerInterestPtr.delete_status = True
		buyerInterestPtr.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer": "buyer interest deleted"})