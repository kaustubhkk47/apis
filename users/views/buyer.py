from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string, validate_integer, validate_bool, getArrFromString
import json

from ..models.buyer import *
from catalog.models.category import Category
from catalog.models.product import Product
from ..serializers.buyer import *
from django.core.paginator import Paginator

import logging
log = logging.getLogger("django")

def get_buyer_details(request,buyerParameters):
	try:
		buyers = filterBuyer(buyerParameters)

		response = {
			"buyers" : parse_buyer(buyers, buyerParameters)
		}
		closeDBConnection()

		return customResponse("2XX", response)
	except Exception as e:
		log.critical(e)
		return customResponse("4XX", {"error": "Invalid request"})

def get_buyer_shared_product_id_details(request,buyerParameters):
	try:
		buyerSharedProductID = filterBuyerSharedProductID(buyerParameters)

		response = {
			"buyer_shared_product_id" : parse_buyer_shared_product_id(buyerSharedProductID, buyerParameters)
		}
		closeDBConnection()

		return customResponse("2XX", response)
	except Exception as e:
		log.critical(e)
		return customResponse("4XX", {"error": "Invalid request"})

def get_buyer_interest_details(request,buyerParameters):
	try:
		buyerInterests = filterBuyerInterest(buyerParameters)

		response = {
			"buyer_interests" : parse_buyer_interest(buyerInterests, buyerParameters)
		}
		closeDBConnection()

		return customResponse("2XX", response)
	except Exception as e:
		log.critical(e)
		return customResponse("4XX", {"error": "Invalid request"})

def get_buyer_product_details(request, buyerParameters):
	try:
		buyerProducts = filterBuyerProducts(buyerParameters)

		paginator = Paginator(buyerProducts, buyerParameters["itemsPerPage"])

		try:
			pageItems = paginator.page(buyerParameters["pageNumber"])
		except Exception as e:
			pageItems = []

		body = parse_buyer_product(pageItems,buyerParameters)
		statusCode = "2XX"
		response = {"buyer_products": body,"total_items":paginator.count, "total_pages":paginator.num_pages, "page_number":buyerParameters["pageNumber"], "items_per_page":buyerParameters["itemsPerPage"]}

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

		BuyerProducts.objects.filter(product_id__in=intersectingProducts[1],buyer_id=buyerPtr.id).update(buyer_interest=newBuyerInterest,delete_status=False)

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer_interest" : serialize_buyer_interest(newBuyerInterest)})

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

		BuyerProducts.objects.filter(product_id__in=intersectingProducts[1],buyer_id=buyerPtr.id).update(is_active=True,delete_status=False)

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

		BuyerProducts.objects.filter(product_id__in=intersectingProducts[1],buyer_id=buyerInterestPtr.buyer_id).update(buyer_interest=buyerInterestPtr,delete_status=False)

		BuyerProducts.objects.filter(product_id__in=intersectingProducts[2],buyer_id=buyerInterestPtr.buyer_id).update(delete_status=True)

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
