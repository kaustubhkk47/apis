from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string, validate_integer, validate_bool, getArrFromString
import json

from ...models.buyer import *
from catalog.models.category import Category
from catalog.models.product import Product
from address.models.state import State
from ...serializers.buyer import *
from ...models.businessType import *
from django.core.paginator import Paginator
from django.utils import timezone

import logging
log = logging.getLogger("django")

import time

from pandas import DataFrame

def get_buyer_shared_product_id_details(request,parameters = {}):
	try:
		buyerSharedProductID = filterBuyerSharedProductID(parameters)

		response = {
			"buyer_shared_product_id" : parse_buyer_shared_product_id(buyerSharedProductID, parameters)
		}
		closeDBConnection()

		return customResponse(200, response)
	except Exception as e:
		log.critical(e)
		return customResponse(500)

def get_buyer_product_details(request, parameters = {}):
	try:
		parameters["buyer_product_delete_status"] = False
		parameters["buyer_interest_active"] = True
		parameters["responded"] = 0
		buyerProducts = filterBuyerProducts(parameters)

		paginator = Paginator(buyerProducts, parameters["itemsPerPage"])

		try:
			pageItems = paginator.page(parameters["pageNumber"])
		except Exception as e:
			pageItems = []

		body = parse_buyer_product(pageItems,parameters)
		statusCode = 200
		response = {"buyer_products": body}

		responsePaginationParameters(response, paginator, parameters)

	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response)

def get_buyer_product_response_details(request, parameters = {}):
	try:
		buyerProductResponse = filterBuyerProductResponse(parameters)

		paginator = Paginator(buyerProductResponse, parameters["itemsPerPage"])

		try:
			pageItems = paginator.page(parameters["pageNumber"])
		except Exception as e:
			pageItems = []

		body = parse_buyer_product_response(pageItems,parameters)
		statusCode = 200
		response = {"buyer_products": body}

		responsePaginationParameters(response, paginator, parameters)

	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response)

def post_new_buyer_product(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_product = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_product):
		return customResponse(400, error_code=5, error_details=  "Invalid data sent in request")

	buyerParameters = {}
	buyerParameters["test_buyer"] = False
	buyerParameters["whatsapp_sharing_active"] = True

	if "all_buyers" in buyer_product and validate_bool(buyer_product["all_buyers"]) and int(buyer_product["all_buyers"])==1:		
		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)
	else:
		if parameters["isBuyer"] == 1:
			buyer_product["buyerID"] = parameters["buyersArr"][0]
		elif not "buyerID" in buyer_product:
			return customResponse(400, error_code=5, error_details= "Id for buyer not sent")
		buyerParameters["buyersArr"] = getArrFromString(buyer_product["buyerID"])

	allBuyersSeries = filterBuyer(buyerParameters).values_list('id', flat=True)

	if len(allBuyersSeries) == 0:
		return customResponse(400, error_code=6, error_details=  "Invalid ids for buyer sent")

	if not "productID" in buyer_product or buyer_product["productID"]==None:
		return customResponse(400, error_code=5, error_details= "Id for product not sent")

	productParameters = {}
	productParameters["product_verification"] = True
	productParameters["product_show_online"] = True
	productParameters["productsArr"] = getArrFromString(buyer_product["productID"])

	allProductsDF = filterProducts(productParameters).values('id')
	if len(allProductsDF) == 0:
		return customResponse(400, error_code=6, error_details=  "Invalid ids for products sent")
	allProductsDF = DataFrame(list(allProductsDF))

	#buyerProductsPtr = BuyerProducts.objects.filter(buyer_id__in = allBuyersSeries).order_by('buyer_id')

	buyerProductParameters = {}
	buyerProductParameters["buyersArr"] = allBuyersSeries
	#buyerProductParameters["responded"] = 0

	allBuyerProductsDF = filterBuyerProducts(buyerProductParameters).values('id','buyer_id', 'product_id', 'responded')
	if len(allBuyerProductsDF) == 0:
		columns = ['id','buyer_id','product_id','responded']
		allBuyerProductsDF = DataFrame(columns=columns)
	else:
		allBuyerProductsDF = DataFrame(list(allBuyerProductsDF))

	buyerProductsToCreate = []
	buyerProductsToUpdate = []
	buyerSharedProductIDtoCreate = []

	for buyer in allBuyersSeries:
		tempBuyerProductsDF = allBuyerProductsDF[allBuyerProductsDF.buyer_id==buyer]
		innerFrame = tempBuyerProductsDF[(tempBuyerProductsDF.product_id.isin(allProductsDF.id))]	
		leftOnlyFrame = allProductsDF[(~allProductsDF.id.isin(innerFrame.product_id))]
				
		for product_id in leftOnlyFrame['id'].tolist():
			buyerProduct = BuyerProducts(buyer_id=buyer, product_id=product_id, buyer_interest=None)
			buyerProductsToCreate.append(buyerProduct)
	
		buyerProductsToUpdate.extend(innerFrame['id'].tolist())

		newBuyerSharedProductID = BuyerSharedProductID(buyer_id=buyer, productid_filter_text=buyer_product["productID"])
		buyerSharedProductIDtoCreate.append(newBuyerSharedProductID)

	try:

		BuyerSharedProductID.objects.bulk_create(buyerSharedProductIDtoCreate,batch_size=4000)
		
		BuyerProducts.objects.bulk_create(buyerProductsToCreate,batch_size=4000)

		BuyerProducts.objects.filter(id__in=buyerProductsToUpdate).update(is_active=True,delete_status=False, updated_at = timezone.now())

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer_product":"successfully added"})

def update_buyer_product_response(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_product_response = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_product_response):
		return customResponse(400, error_code=5,  error_details= "Invalid data sent in request")

	if parameters["isBuyer"] == 1:
		buyer_product_response["buyerID"] = parameters["buyersArr"][0]
	elif not "buyerID" in buyer_product_response or not validate_integer(buyer_product_response["buyerID"]):
		return customResponse(400, error_code=5,  error_details= "Id for buyer not sent")

	buyerParameters = {"buyersArr":[int(buyer_product_response["buyerID"])]}
	buyerPtr = filterBuyer(buyerParameters)

	if not buyerPtr.exists():
		return customResponse(400, error_code=6,  error_details= "Invalid id for buyer sent")

	if not "productID" in buyer_product_response or not validate_integer(buyer_product_response["productID"]):
		return customResponse(400, error_code=5,  error_details=  "Id for product not sent")

	#productParameters = {"productsArr":[int(buyer_product["productID"])]}
	productPtr = Product.objects.filter(id=int(buyer_product_response["productID"]))

	if not productPtr.exists():
		return customResponse(400, error_code=6,  error_details= "Invalid id for product sent")

	buyerProductResponsePtr = BuyerProductResponse.objects.filter(buyer_id = int(buyer_product_response["buyerID"]), product_id = int(buyer_product_response["productID"]))

	if len(buyerProductResponsePtr) == 0:
		return customResponse(400, error_code=6,  error_details=  "Invalid id for product and buyer sent")

	buyerProductResponsePtr = buyerProductResponsePtr[0]
	

	if not buyerProductResponsePtr.validateBuyerProductResponseData(buyer_product_response):
		return customResponse(400, error_code=5,  error_details= "Invalid data for buyer product response sent")

	try:
		
		buyerProductResponsePtr.populateBuyerProductResponse(buyer_product_response)
		buyerProductResponsePtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer_product_response" : serialize_buyer_product_response(buyerProductResponsePtr, parameters)})

def update_buyer_product(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_product = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_product):
		return customResponse(400, error_code=5,  error_details="Invalid data sent in request")

	if parameters["isBuyer"] == 1:
		buyer_product["buyerID"] = parameters["buyersArr"][0]
	elif not "buyerID" in buyer_product or not validate_integer(buyer_product["buyerID"]):
		return customResponse(400, error_code=5,  error_details="Id for buyer not sent")

	buyerParameters = {"buyersArr":[int(buyer_product["buyerID"])]}
	buyerPtr = filterBuyer(buyerParameters)

	if not buyerPtr.exists():
		return customResponse(400, error_code=6,  error_details= "Invalid id for buyer sent")

	if not "productID" in buyer_product or not validate_integer(buyer_product["productID"]):
		return customResponse(400, error_code=5,  error_details= "Id for product not sent")

	#productParameters = {"productsArr":[int(buyer_product["productID"])]}
	productPtr = Product.objects.filter(id=int(buyer_product["productID"]))

	if not productPtr.exists():
		return customResponse(400, error_code=6,  error_details= "Invalid id for product sent")

	buyerProductPtr = BuyerProducts.objects.filter(buyer_id = int(buyer_product["buyerID"]), product_id = int(buyer_product["productID"]))

	if len(buyerProductPtr) > 0:
		buyerProductPtr = buyerProductPtr[0]
	else:
		buyerProductPtr = BuyerProducts(buyer_id = int(buyer_product["buyerID"]), product_id = int(buyer_product["productID"]), shared_on_whatsapp=True)

	buyer_product_populator = {}

	if not validateBuyerProductData(buyer_product, buyerProductPtr, 0, buyer_product_populator):
		return customResponse(400, error_code=5,  error_details= "Invalid data for buyer product sent")

	try:
		
		populateBuyerProduct(buyerProductPtr, buyer_product_populator)
		buyerProductPtr.save()

		if "response_code" in buyer_product_populator:
			newBuyerProductResponseHistory = BuyerProductResponseHistory(buyer_id=buyerProductPtr.buyer_id,product_id=buyerProductPtr.product_id,buyer_product_id=buyerProductPtr.id)
			populateBuyerProductResponseHistory(newBuyerProductResponseHistory,buyer_product_populator)
			newBuyerProductResponseHistory.save()

			BuyerProductResponsePtr = BuyerProductResponse.objects.filter(buyer_id=buyerProductPtr.buyer_id,product_id=buyerProductPtr.product_id)

			if len(BuyerProductResponsePtr) == 0:
				BuyerProductResponsePtr = BuyerProductResponse(buyer_id=buyerProductPtr.buyer_id,product_id=buyerProductPtr.product_id,buyer_product_id=buyerProductPtr.id)
			else:
				BuyerProductResponsePtr = BuyerProductResponsePtr[0]

			if not "has_swiped" in buyer_product_populator:
				buyer_product_populator["has_swiped"] = 0
			if buyer_product_populator["response_code"] == 3:
				buyer_product_populator["response_code"] = 1
			elif buyer_product_populator["response_code"] == 4:
				buyer_product_populator["response_code"] = 2
			populateBuyerProductResponse(BuyerProductResponsePtr, buyer_product_populator)
			BuyerProductResponsePtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer_product_response" : serialize_buyer_product_response(BuyerProductResponsePtr)})

def update_buyer_product_whatsapp(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_product = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_product) or not "buyerproductID" in buyer_product or buyer_product["buyerproductID"]==None:
		return customResponse(400, error_code=5,  error_details= "Id for buyer product not sent")

	

	buyerProductIDs = getArrFromString(str(buyer_product["buyerproductID"]))

	buyerProductPtr = BuyerProducts.objects.filter(id__in=buyerProductIDs)

	if parameters["isBuyer"] == 1:
		buyerProductPtr.filter(buyer_id=parameters["buyersArr"][0])

	if len(buyerProductPtr) != len(buyerProductIDs):
		return customResponse(400, error_code=6,  error_details=  "Invalid ids for for buyer products sent")

	try:
		
		buyerProductPtr.update(shared_on_whatsapp=True,  updated_at = timezone.now())

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"success" : "updated"})

def post_buyer_product_landing(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_product = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_product) or not "buyerproductID" in buyer_product or not validate_integer(buyer_product["buyerproductID"]):
		return customResponse(400, error_code=5, error_details="Id for buyer product not sent")

	buyerProductPtr = BuyerProducts.objects.filter(id=int(buyer_product["buyerproductID"]))

	if len(buyerProductPtr) == 0:
		return customResponse(400, error_code=6, error_details="Invalid id for for buyer product sent")

	buyerProductPtr = buyerProductPtr[0]

	try:
		newBuyerProductLanding = BuyerProductLanding(buyer_id=buyerProductPtr.buyer_id, product_id=buyerProductPtr.product_id,buyer_product_id=buyerProductPtr.id)
		newBuyerProductLanding.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"success" : "created"})

def master_update_buyer_product(request):

	try:

		buyerInterestParameters = {}
		buyerInterestParameters["is_active"] = True
		buyerInterestParameters["buyer_whatsapp_sharing_active"] = True
		allBuyerInterestsDF = filterBuyerInterest(buyerInterestParameters).values('id', 'buyer_id', 'category_id', 'price_filter_applied','min_price_per_unit','max_price_per_unit','fabric_filter_text')
		if len(allBuyerInterestsDF) == 0:
			return customResponse(200, {"success" : "Already updated"})

		allBuyerInterestsDF = DataFrame(list(allBuyerInterestsDF))
		log.critical("master_update_buyer_product 1 reached")
		allBuyerInterestsDF['fabricArr'] = allBuyerInterestsDF.fabric_filter_text.str.replace(" ","").str.lower().str.split(",")
	
		allBuyersSeries = allBuyerInterestsDF.buyer_id.unique()
		log.critical("master_update_buyer_product 2 reached")
	
		productParameters = {}
		productParameters["product_verification"] = True
		productParameters["product_show_online"] = True
		productParameters["product_new_in_product_matrix"] = True

		allProductsDF = filterProducts(productParameters).values('id','category_id','min_price_per_unit', 'productdetails__fabric_gsm')
		if len(allProductsDF) == 0:
			return customResponse(200, {"success" : "Already updated"})
		allProductsDF = DataFrame(list(allProductsDF))
		log.critical("master_update_buyer_product 3 reached")
		allProductsDF['productdetails__fabric_gsm'] = allProductsDF['productdetails__fabric_gsm'].str.replace(" ","").str.lower()

		buyerProductParameters = {}
		buyerProductParameters["product_new_in_product_matrix"] = True
		buyerProductParameters["buyersArr"] = list(allBuyersSeries)

		allBuyerProductsDF = filterBuyerProducts(buyerProductParameters).values('id','buyer_id', 'product_id', 'buyer_interest_id', 'responded')
		if len(allBuyerProductsDF) == 0:
			columns = ['buyer_id','buyer_interest_id','id','product_id','responded']
			allBuyerProductsDF = DataFrame(columns=columns)
		else:
			allBuyerProductsDF = DataFrame(list(allBuyerProductsDF))

		log.critical("master_update_buyer_product 4 reached")
	
		#  Buyer ID, BuyerInterestID, Set of product ID
		buyerProductsToCreate = []
		# BuyerInterestID, set of BuyerproductID
		middleSet = []
		#BuyerproductID
		rightSet = []
	
		for buyer in allBuyersSeries:
			tempBuyerProductsDF = allBuyerProductsDF[allBuyerProductsDF.buyer_id==buyer]
			tempBuyerInterestsDF = allBuyerInterestsDF[allBuyerInterestsDF.buyer_id==buyer]
			for row in tempBuyerInterestsDF.itertuples():
				tempProductsDF = allProductsDF[(allProductsDF.category_id==row[2])&(allProductsDF.productdetails__fabric_gsm.str.contains('|'.join(row[8])))]
				if row[7] == True:
					tempProductsDF = tempProductsDF[(tempProductsDF.min_price_per_unit>=row[6])&(tempProductsDF.min_price_per_unit<=row[5])]
				innerFrame = tempBuyerProductsDF[(tempBuyerProductsDF.product_id.isin(tempProductsDF.id))]
				leftOnlyFrame = tempProductsDF[(~tempProductsDF.id.isin(innerFrame.product_id))]
				rightOnlyFrame = tempBuyerProductsDF[(~tempBuyerProductsDF.id.isin(innerFrame.id))&(tempBuyerProductsDF.responded==0)]
				
				for product_id in leftOnlyFrame['id'].tolist():
					buyerProduct = BuyerProducts(buyer_id=buyer, product_id=product_id, buyer_interest_id=row[4])
					buyerProductsToCreate.append(buyerProduct)
	
				middleSet.append([row[4], innerFrame['id'].tolist()])
				rightSet.extend(rightOnlyFrame['id'].tolist())

		del(allBuyerProductsDF)
		del(allProductsDF)
		del(allBuyerInterestsDF)
		del(allBuyersSeries)
		log.critical("master_update_buyer_product 5 reached")
		
		BuyerProducts.objects.bulk_create(buyerProductsToCreate, batch_size=4000)
		del(buyerProductsToCreate)
		log.critical("master_update_buyer_product 6 reached")

		for row in middleSet:
			BuyerProducts.objects.filter(id__in=row[1]).update(buyer_interest_id=row[0],delete_status=False,  updated_at = timezone.now())
		del(middleSet)
		log.critical("master_update_buyer_product 7 reached")
		BuyerProducts.objects.filter(id__in=rightSet).update(delete_status=True, buyer_interest_id=None, updated_at = timezone.now())
		del(rightSet)
		log.critical("master_update_buyer_product 8 reached")
		filterProducts(productParameters).update(new_in_product_matrix=False, updated_at = timezone.now())
		log.critical("master_update_buyer_product 9 reached")

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"success" : "updated"})

def delete_buyer_shared_product_id(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_shared_product_id = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyer_shared_product_id) or not "buyersharedproductID" in buyer_shared_product_id or not validate_integer(buyer_shared_product_id["buyersharedproductID"]):
		return customResponse(400, error_code=5,  error_details= "Id for buyer shared_product_id not sent")

	buyerSharedProductIDPtr = BuyerSharedProductID.objects.filter(id=int(buyer_shared_product_id["buyersharedproductID"]))

	if len(buyerSharedProductIDPtr) == 0:
		return customResponse(400, error_code=6,  error_details= "Invalid id for buyer shared_product_id sent")

	buyerSharedProductIDPtr = buyerSharedProductIDPtr[0]

	try:
		buyerSharedProductIDPtr.delete_status = True
		buyerSharedProductIDPtr.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer": "buyer shared_product_id deleted"})