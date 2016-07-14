from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string, validate_integer, validate_bool, getArrFromString
import json

from ..models.buyer import *
from catalog.models.category import Category
from catalog.models.product import Product
from address.models.state import State
from ..serializers.buyer import *
from ..models.businessType import *
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

		return customResponse("2XX", response)
	except Exception as e:
		log.critical(e)
		return customResponse("4XX", {"error": "Invalid request"})

def get_buyer_purchasing_state_details(request,parameters = {}):
	try:
		buyersPurchasingState = filterBuyerPurchasingState(parameters)

		response = {
			"buyer_purchasing_states" : parse_buyer_purchasing_state(buyersPurchasingState, parameters)
		}
		closeDBConnection()

		return customResponse("2XX", response)
	except Exception as e:
		log.critical(e)
		return customResponse("4XX", {"error": "Invalid request"})

def get_buyer_buys_from_details(request,parameters = {}):
	try:
		buyerBuysFrom = filterBuyerBuysFrom(parameters)

		response = {
			"buyer_buys_from" : parse_buyer_buys_from(buyerBuysFrom, parameters)
		}
		closeDBConnection()

		return customResponse("2XX", response)
	except Exception as e:
		log.critical(e)
		return customResponse("4XX", {"error": "Invalid request"})

def get_buyer_access_token_details(request,parameters = {}):
	try:
		buyerPanelURL = parameters["buyer_panel_url"].split("-")
		try:
			buyerID = int(buyerPanelURL[0])
			timeStamp = int(buyerPanelURL[1])
		except Exception as e:
			return customResponse("4XX", {"error": "Invalid data in request sent"})

		buyerPtr = Buyer.objects.get(id=buyerID)

		if int(time.mktime(buyerPtr.created_at.timetuple())) != timeStamp:
			closeDBConnection()
			return customResponse("4XX", {"error": "Invalid time sent"})

		from urlHandlers.user_handler import getBuyerToken

		response = {
			"token" : getBuyerToken(buyerPtr)
		}
		closeDBConnection()

		return customResponse("2XX", response)
	except Exception as e:
		closeDBConnection()
		log.critical(e)
		return customResponse("4XX", {"error": "Invalid request"})

def get_buyer_shared_product_id_details(request,parameters = {}):
	try:
		buyerSharedProductID = filterBuyerSharedProductID(parameters)

		response = {
			"buyer_shared_product_id" : parse_buyer_shared_product_id(buyerSharedProductID, parameters)
		}
		closeDBConnection()

		return customResponse("2XX", response)
	except Exception as e:
		log.critical(e)
		return customResponse("4XX", {"error": "Invalid request"})

def get_buyer_interest_details(request,parameters = {}):
	try:
		buyerInterests = filterBuyerInterest(parameters)

		response = {
			"buyer_interests" : parse_buyer_interest(buyerInterests, parameters)
		}
		closeDBConnection()

		return customResponse("2XX", response)
	except Exception as e:
		log.critical(e)
		return customResponse("4XX", {"error": "Invalid request"})

def get_buyer_product_details(request, parameters = {}):
	try:
		parameters["buyer_product_delete_status"] = False
		parameters["buyer_interest_active"] = True
		buyerProducts = filterBuyerProducts(parameters)

		paginator = Paginator(buyerProducts, parameters["itemsPerPage"])

		try:
			pageItems = paginator.page(parameters["pageNumber"])
		except Exception as e:
			pageItems = []

		body = parse_buyer_product(pageItems,parameters)
		statusCode = "2XX"
		response = {"buyer_products": body,"total_items":paginator.count, "total_pages":paginator.num_pages, "page_number":parameters["pageNumber"], "items_per_page":parameters["itemsPerPage"]}

	except Exception as e:
		log.critical(e)
		statusCode = "4XX"
		response = {"error": "Invalid request"}

	closeDBConnection()
	return customResponse(statusCode, response)

def post_new_buyer(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer) or not validateBuyerData(buyer, Buyer(), 1):
		return customResponse("4XX", {"error": "Invalid data for buyer sent"})

	if buyer["email"] != None and buyerEmailExists(buyer["email"]):
		return customResponse("4XX", {"error": "buyer email already exists"})

	if buyerMobileNumberExists(buyer["mobile_number"]):
		return customResponse("4XX", {"error": "buyer phone number already exists"})

	if not "address" in buyer or buyer["address"]==None:
		buyer["address"] = {}
		
	validateBuyerAddressData(buyer["address"], BuyerAddress())

	if not "details" in buyer or buyer["details"]==None:
		buyer["details"] = {}

	validateBuyerDetailsData(buyer["details"], BuyerDetails(), 1)

	try:
		newBuyer = Buyer()

		populateBuyer(newBuyer, buyer)
		newBuyer.save()
		newBuyer.whatsapp_contact_name = str(newBuyer.id) + " Wholdus " + newBuyer.name
		newBuyer.save()

		buyeraddress = buyer["address"]
		newAddress = BuyerAddress(buyer=newBuyer)
		populateBuyerAddress(newAddress, buyeraddress)

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
		 
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer" : serialize_buyer(newBuyer)})

def post_new_buyer_interest(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_interest = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer_interest) or not "buyerID" in buyer_interest or buyer_interest["buyerID"]==None or not validate_integer(buyer_interest["buyerID"]):
		return customResponse("4XX", {"error": "Id for buyer not sent"})

	buyerPtr = Buyer.objects.filter(id=int(buyer_interest["buyerID"]))

	if len(buyerPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for buyer sent"})

	buyerPtr = buyerPtr[0]

	if not "categoryID" in buyer_interest or buyer_interest["categoryID"]==None or not validate_integer(buyer_interest["categoryID"]):
		return customResponse("4XX", {"error": "Id for category not sent"})

	categoryPtr = Category.objects.filter(id=int(buyer_interest["categoryID"]))

	if len(categoryPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for category sent"})

	categoryPtr = categoryPtr[0]

	BuyerInterestPtr = BuyerInterest.objects.filter(buyer_id=buyerPtr.id,category_id=categoryPtr.id)

	if len(BuyerInterestPtr)>0:
		return customResponse("4XX", {"error": "Buyer interest for category already exists"})

	if not validateBuyerInterestData(buyer_interest, BuyerInterest(), 1):
		return customResponse("4XX", {"error": "Invalid data for buyer interest sent"})

	try:
		newBuyerInterest = BuyerInterest(buyer=buyerPtr,category=categoryPtr)
		populateBuyerInterest(newBuyerInterest, buyer_interest)
		newBuyerInterest.save()

		newBuyerInterestHistory = BuyerInterestHistory(buyer_interest=newBuyerInterest)
		populateBuyerInterest(newBuyerInterestHistory, buyer_interest)
		newBuyerInterestHistory.save()

		productPtr = filterBuyerInterestProducts(newBuyerInterest)

		buyerProductPtr = BuyerProducts.objects.filter(buyer_id = buyerPtr.id)

		intersectingProducts = getIntersectingProducts(productPtr, buyerProductPtr)

		buyerProductsToCreate = []

		for product_id in intersectingProducts[0]:
			buyerProduct = BuyerProducts(buyer=buyerPtr, product_id=product_id, buyer_interest=newBuyerInterest)
			buyerProductsToCreate.append(buyerProduct)

		BuyerProducts.objects.bulk_create(buyerProductsToCreate)

		BuyerProducts.objects.filter(id__in=intersectingProducts[1]).update(buyer_interest=newBuyerInterest,delete_status=False)

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer_interest" : serialize_buyer_interest(newBuyerInterest)})

def post_new_buyer_purchasing_state(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_purchasing_state = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer_purchasing_state) or not "buyerID" in buyer_purchasing_state or buyer_purchasing_state["buyerID"]==None or not validate_integer(buyer_purchasing_state["buyerID"]):
		return customResponse("4XX", {"error": "Id for buyer not sent"})

	buyerPtr = Buyer.objects.filter(id=int(buyer_purchasing_state["buyerID"]))

	if len(buyerPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for buyer sent"})

	buyerPtr = buyerPtr[0]

	if not "stateID" in buyer_purchasing_state or buyer_purchasing_state["stateID"]==None or not validate_integer(buyer_purchasing_state["stateID"]):
		return customResponse("4XX", {"error": "Id for state not sent"})

	statePtr = State.objects.filter(id=int(buyer_purchasing_state["stateID"]))

	if len(statePtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for state sent"})

	statePtr = statePtr[0]

	BuyerPurchasingStatePtr = BuyerPurchasingState.objects.filter(buyer_id=buyerPtr.id,state_id=statePtr.id)

	if len(BuyerPurchasingStatePtr)>0:
		BuyerPurchasingStatePtr = BuyerPurchasingStatePtr[0]
		if BuyerPurchasingStatePtr.delete_status == True:
			BuyerPurchasingStatePtr.delete_status = False
			BuyerPurchasingStatePtr.save()
			closeDBConnection()
			return customResponse("2XX", {"buyer_purchasing_state" : serialize_buyer_purchasing_state(BuyerPurchasingStatePtr)})
		else:
			return customResponse("4XX", {"error": "Buyer purchasing_state already exists"})

	try:
		newBuyerPurchasingState = BuyerPurchasingState(buyer=buyerPtr,state=statePtr)
		newBuyerPurchasingState.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer_purchasing_state" : serialize_buyer_purchasing_state(newBuyerPurchasingState)})

def post_new_buyer_buys_from(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_buys_from = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer_buys_from) or not "buyerID" in buyer_buys_from or buyer_buys_from["buyerID"]==None or not validate_integer(buyer_buys_from["buyerID"]):
		return customResponse("4XX", {"error": "Id for buyer not sent"})

	buyerPtr = Buyer.objects.filter(id=int(buyer_buys_from["buyerID"]))

	if len(buyerPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for buyer sent"})

	buyerPtr = buyerPtr[0]

	if not "businesstypeID" in buyer_buys_from or buyer_buys_from["businesstypeID"]==None or not validate_integer(buyer_buys_from["businesstypeID"]):
		return customResponse("4XX", {"error": "Id for state not sent"})

	businessTypePtr = BusinessType.objects.filter(id=int(buyer_buys_from["businesstypeID"]), can_buyer_buy_from=True)

	if len(businessTypePtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for business type sent"})

	businessTypePtr = businessTypePtr[0]

	BuyerBuysFromPtr = BuyerBuysFrom.objects.filter(buyer_id=buyerPtr.id,business_type_id=businessTypePtr.id)

	if len(BuyerBuysFromPtr)>0:
		BuyerBuysFromPtr = BuyerBuysFromPtr[0]
		if BuyerBuysFromPtr.delete_status == True:
			BuyerBuysFromPtr.delete_status = False
			BuyerBuysFromPtr.save()
			closeDBConnection()
			return customResponse("2XX", {"buyer_buys_from" : serialize_buyer_buys_from(BuyerBuysFromPtr)})
		else:
			return customResponse("4XX", {"error": "Buyer buys_from already exists"})

	try:
		newBuyerBuysFrom = BuyerBuysFrom(buyer=buyerPtr,business_type=businessTypePtr)
		newBuyerBuysFrom.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer_buys_from" : serialize_buyer_buys_from(newBuyerBuysFrom)})

def post_new_buyer_product(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_product = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer_product) or not "buyerID" in buyer_product or buyer_product["buyerID"]==None or not validate_integer(buyer_product["buyerID"]):
		return customResponse("4XX", {"error": "Id for buyer not sent"})

	buyerPtr = Buyer.objects.filter(id=int(buyer_product["buyerID"]))

	if len(buyerPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for buyer sent"})

	buyerPtr = buyerPtr[0]

	if not "productID" in buyer_product or buyer_product["productID"]==None:
		return customResponse("4XX", {"error": "Id for product not sent"})

	productIDs = getArrFromString(buyer_product["productID"])

	productPtr = Product.objects.filter(delete_status=False, seller__delete_status=False, category__delete_status=False, verification=True,show_online=True,seller__show_online=True, id__in=productIDs)

	if len(productPtr) == 0:
		return customResponse("4XX", {"error": "Invalid ids for products sent"})

	buyerProductsPtr = BuyerProducts.objects.filter(buyer_id = int(buyer_product["buyerID"]))

	intersectingProducts = getIntersectingProducts(productPtr, buyerProductsPtr)

	buyerProductsToCreate = []

	for product_id in intersectingProducts[0]:
		buyerProduct = BuyerProducts(buyer=buyerPtr, product_id=product_id, buyer_interest=None)
		buyerProductsToCreate.append(buyerProduct)

	try:

		newBuyerSharedProductID = BuyerSharedProductID(buyer=buyerPtr, productid_filter_text=buyer_product["productID"])
		newBuyerSharedProductID.save()
		
		BuyerProducts.objects.bulk_create(buyerProductsToCreate)

		BuyerProducts.objects.filter(id__in=intersectingProducts[1]).update(is_active=True,delete_status=False)

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer_product":"successfully added"})

def update_buyer_interest(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_interest = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer_interest) or not "buyerinterestID" in buyer_interest or buyer_interest["buyerinterestID"]==None or not validate_integer(buyer_interest["buyerinterestID"]):
		return customResponse("4XX", {"error": "Id for buyer interest not sent"})

	buyerInterestPtr = BuyerInterest.objects.filter(id=int(buyer_interest["buyerinterestID"]))

	if len(buyerInterestPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id interest for buyer sent"})

	buyerInterestPtr = buyerInterestPtr[0]

	if not validateBuyerInterestData(buyer_interest, buyerInterestPtr, 0):
		return customResponse("4XX", {"error": "Invalid data for buyer interest sent"})

	buyerProductPtr = BuyerProducts.objects.filter(buyer_interest_id = buyerInterestPtr.id)

	forceEvaluation = len(buyerProductPtr)

	try:
		
		populateBuyerInterest(buyerInterestPtr, buyer_interest)
		buyerInterestPtr.save()

		newBuyerInterestHistory = BuyerInterestHistory(buyer_interest=buyerInterestPtr)
		populateBuyerInterest(newBuyerInterestHistory, buyer_interest)
		newBuyerInterestHistory.save()

		productPtr = filterBuyerInterestProducts(buyerInterestPtr)

		intersectingProducts = getIntersectingProducts(productPtr, buyerProductPtr)

		buyerProductsToCreate = []

		for product_id in intersectingProducts[0]:
			buyerProduct = BuyerProducts(buyer_id=buyerInterestPtr.buyer_id, product_id=product_id, buyer_interest=buyerInterestPtr)
			buyerProductsToCreate.append(buyerProduct)

		BuyerProducts.objects.bulk_create(buyerProductsToCreate)

		BuyerProducts.objects.filter(id__in=intersectingProducts[1]).update(buyer_interest=buyerInterestPtr,delete_status=False)

		BuyerProducts.objects.filter(id__in=intersectingProducts[2],responded=0).update(delete_status=True, buyer_interest_id=None)

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer" : serialize_buyer_interest(buyerInterestPtr)})

def update_buyer_product(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_product = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer_product) or not "buyerproductID" in buyer_product or buyer_product["buyerproductID"]==None or not validate_integer(buyer_product["buyerproductID"]):
		return customResponse("4XX", {"error": "Id for buyer product not sent"})

	buyerProductPtr = BuyerProducts.objects.filter(id=int(buyer_product["buyerproductID"]))

	if len(buyerProductPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id product for buyer sent"})

	buyerProductPtr = buyerProductPtr[0]

	buyer_product_populator = {}

	if not validateBuyerProductData(buyer_product, buyerProductPtr, 0, buyer_product_populator):
		return customResponse("4XX", {"error": "Invalid data for buyer product sent"})

	try:
		
		populateBuyerProduct(buyerProductPtr, buyer_product_populator)
		buyerProductPtr.save()

		if "response_code" in buyer_product_populator:
			newBuyerProductResponseHistory = BuyerProductResponseHistory(buyer_id=buyerProductPtr.buyer_id,product_id=buyerProductPtr.product_id,buyer_product_id=buyerProductPtr.id)
			populateBuyerProductResponseHistory(newBuyerProductResponseHistory,buyer_product_populator)
			newBuyerProductResponseHistory.save()

			if buyer_product_populator["response_code"] == 1 or  buyer_product_populator["response_code"] == 2:
				newBuyerProductResponse = BuyerProductResponse(buyer_id=buyerProductPtr.buyer_id,product_id=buyerProductPtr.product_id,buyer_product_id=buyerProductPtr.id)
				populateBuyerProductResponse(newBuyerProductResponse, buyer_product_populator)
				newBuyerProductResponse.save()
			elif buyer_product_populator["response_code"] == 3:
				try:
					BuyerProductResponsePtr = BuyerProductResponse.objects.filter(buyer_id=buyerProductPtr.buyer_id,product_id=buyerProductPtr.product_id)
					if len(BuyerProductResponsePtr) > 0:
						BuyerProductResponsePtr = BuyerProductResponsePtr[0]
						BuyerProductResponsePtr.response_code = 1
						BuyerProductResponsePtr.save()
				except Exception as e:
					pass

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer_products" : serialize_buyer_product(buyerProductPtr)})

def update_buyer_product_whatsapp(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_product = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer_product) or not "buyerproductID" in buyer_product or buyer_product["buyerproductID"]==None:
		return customResponse("4XX", {"error": "Id for buyer product not sent"})

	buyerProductIDs = getArrFromString(str(buyer_product["buyerproductID"]))

	buyerProductPtr = BuyerProducts.objects.filter(id__in=buyerProductIDs)

	if len(buyerProductPtr) != len(buyerProductIDs):
		return customResponse("4XX", {"error": "Invalid ids for for buyer products sent"})

	try:
		
		buyerProductPtr.update(shared_on_whatsapp=True)

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"success" : "updated"})

def post_buyer_product_landing(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_product = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer_product) or not "buyerproductID" in buyer_product or not validate_integer(buyer_product["buyerproductID"]):
		return customResponse("4XX", {"error": "Id for buyer product not sent"})

	buyerProductPtr = BuyerProducts.objects.filter(id=int(buyer_product["buyerproductID"]))

	if len(buyerProductPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for for buyer product sent"})

	buyerProductPtr = buyerProductPtr[0]

	try:
		newBuyerProductLanding = BuyerProductLanding(buyer_id=buyerProductPtr.buyer_id, product_id=buyerProductPtr.product_id,buyer_product_id=buyerProductPtr.id)
		newBuyerProductLanding.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"success" : "created"})

def master_update_buyer_product(request):

	try:

		buyerInterestParameters = {"is_active":True}
		allBuyerInterests = filterBuyerInterest(buyerInterestParameters).values('id', 'buyer_id', 'category_id', 'price_filter_applied','min_price_per_unit','max_price_per_unit','fabric_filter_text')
		if len(allBuyerInterests) == 0:
			return customResponse("2XX", {"success" : "Already updated"})

		allBuyerInterestsDF = DataFrame(list(allBuyerInterests))
		allBuyerInterestsDF['fabricArr'] = allBuyerInterestsDF.fabric_filter_text.str.replace(" ","").str.lower().str.split(",")
	
		allBuyersSeries = allBuyerInterestsDF.buyer_id.unique()
	
		productParameters = {}
		productParameters["product_verification"] = True
		productParameters["product_show_online"] = True
		productParameters["seller_show_online"] = True
		productParameters["product_new_in_product_matrix"] = True

		allProducts = filterProducts(productParameters).values('id','category_id','min_price_per_unit', 'productdetails__fabric_gsm')
		if len(allProducts) == 0:
			return customResponse("2XX", {"success" : "Already updated"})
		allProductsDF = DataFrame(list(allProducts))
		allProductsDF['productdetails__fabric_gsm'] = allProductsDF['productdetails__fabric_gsm'].str.replace(" ","").str.lower()

		buyerProductParameters = {}
		buyerProductParameters["product_new_in_product_matrix"] = True
		buyerProductParameters["buyersArr"] = list(allBuyersSeries)

		allBuyerProducts = filterBuyerProducts(buyerProductParameters).values('id','buyer_id', 'product_id', 'buyer_interest_id', 'responded')
		if len(allBuyerProducts) == 0:
			columns = ['buyer_id','buyer_interest_id','id','product_id','responded']
			allBuyerProductsDF = DataFrame(columns=columns)
		else:
			allBuyerProductsDF = DataFrame(list(allBuyerProducts))
	
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
		
		BuyerProducts.objects.bulk_create(buyerProductsToCreate)
		for row in middleSet:
			BuyerProducts.objects.filter(id__in=row[1]).update(buyer_interest_id=row[0],delete_status=False)
		BuyerProducts.objects.filter(id__in=rightSet).update(delete_status=True, buyer_interest_id=None)
		allProducts.update(new_in_product_matrix=False)

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"success" : "updated"})

def delete_buyer_interest(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_interest = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer_interest) or not "buyerinterestID" in buyer_interest or buyer_interest["buyerinterestID"]==None or not validate_integer(buyer_interest["buyerinterestID"]):
		return customResponse("4XX", {"error": "Id for buyer interest not sent"})

	buyerInterestPtr = BuyerInterest.objects.filter(id=int(buyer_interest["buyerinterestID"]))

	if len(buyerInterestPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for buyer interest sent"})

	buyerInterestPtr = buyerInterestPtr[0]

	try:
		buyerInterestPtr.delete_status = True
		buyerInterestPtr.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "could not delete"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer": "buyer interest deleted"})

def delete_buyer_purchasing_state(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_purchasing_state = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer_purchasing_state) or not "buyerpurchasingstateID" in buyer_purchasing_state or buyer_purchasing_state["buyerpurchasingstateID"]==None or not validate_integer(buyer_purchasing_state["buyerpurchasingstateID"]):
		return customResponse("4XX", {"error": "Id for buyer purchasing_state not sent"})

	buyerPurchasingStatePtr = BuyerPurchasingState.objects.filter(id=int(buyer_purchasing_state["buyerpurchasingstateID"]))

	if len(buyerPurchasingStatePtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for buyer purchasing_state sent"})

	try:
		buyerPurchasingStatePtr.update(delete_status = True)
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "could not delete"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer": "buyer purchasing_state deleted"})

def delete_buyer_buys_from(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_buys_from = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer_buys_from) or not "buyerbuysfromID" in buyer_buys_from or buyer_buys_from["buyerbuysfromID"]==None or not validate_integer(buyer_buys_from["buyerbuysfromID"]):
		return customResponse("4XX", {"error": "Id for buyer buys_from not sent"})

	buyerBuysFromPtr = BuyerBuysFrom.objects.filter(id=int(buyer_buys_from["buyerbuysfromID"]))

	if len(buyerBuysFromPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for buyer buys_from sent"})

	try:
		buyerBuysFromPtr.update(delete_status = True)
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "could not delete"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer": "buyer buys_from deleted"})

def delete_buyer_shared_product_id(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer_shared_product_id = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer_shared_product_id) or not "buyersharedproductID" in buyer_shared_product_id or buyer_shared_product_id["buyersharedproductID"]==None or not validate_integer(buyer_shared_product_id["buyersharedproductID"]):
		return customResponse("4XX", {"error": "Id for buyer shared_product_id not sent"})

	buyerSharedProductIDPtr = BuyerSharedProductID.objects.filter(id=int(buyer_shared_product_id["buyersharedproductID"]))

	if len(buyerSharedProductIDPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for buyer shared_product_id sent"})

	buyerSharedProductIDPtr = buyerSharedProductIDPtr[0]

	try:
		buyerSharedProductIDPtr.delete_status = True
		buyerSharedProductIDPtr.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "could not delete"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer": "buyer shared_product_id deleted"})

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
				validateBuyerDetailsData(buyerdetails, buyerPtr.buyerdetails, 0)
				populateBuyerDetails(buyerPtr.buyerdetails, buyerdetails)
				if "buyertypeID" in buyer["details"] and validate_integer(buyer["details"]["buyertypeID"]):
					businessTypePtr = BusinessType.objects.filter(id=int(buyer["details"]["buyertypeID"]), can_be_buyer=True)
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
				return customResponse("4XX", {"error": "Address id not sent"})
			buyerAddressPtr = BuyerAddress.objects.filter(id = int(buyeraddress["addressID"]))

			if len(buyerAddressPtr) == 0:
				return customResponse("4XX", {"error": "Invalid address id sent"})

			buyerAddressPtr = buyerAddressPtr[0]

			if(buyerAddressPtr.buyer_id != buyerPtr.id):
				return customResponse("4XX", {"error": "Address id for incorrect buyer sent"})
				
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