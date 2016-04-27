from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string, validate_date_time
import json
from ..models.seller import Seller, SellerAddress, SellerBankDetails, SellerDetails, validateSellerData, validateSellerAddressData, validateSellerDetailsData, validateSellerBankdetailsData, populateSellerData, populateSellerDetailsData,populateSellerAddressData, populateSellerBankDetailsData
from ..serializers.seller import parse_seller, serialize_seller

def get_seller_details(request,sellersArr=[]):
	try:
		if len(sellersArr)==0:

			sellers = Seller.objects.filter(delete_status=False).select_related('sellerdetails')
			closeDBConnection()
		else:
			sellers = Seller.objects.filter(delete_status=False,id__in=sellersArr).select_related('sellerdetails')
			closeDBConnection()

		response = {
			"sellers" : parse_seller(sellers)
		}

		return customResponse("2XX", response)
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid request"})

def post_new_seller(request):
	try:
		requestbody = request.body.decode("utf-8")
		seller = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(seller) or not validateSellerData(seller, Seller(), 1):
		return customResponse("4XX", {"error": "Invalid data for seller sent"})

	if not "address" in seller or not seller["address"]!=None:
		seller["address"] = {}

	validateSellerAddressData(seller["address"], SellerAddress())

	if not "bankdetails" in seller or not seller["bankdetails"]!=None:
		seller["bankdetails"] = {}

	validateSellerBankdetailsData(seller["bankdetails"], SellerBankDetails())

	if not "details" in seller or not seller["details"]!=None:
			seller["details"] = {}

	validateSellerDetailsData(seller["details"], SellerDetails())

	try:
		newSeller = Seller()
		populateSellerData(newSeller, seller)

		newSeller.save()

		selleraddress = seller["address"]
		newAddress = SellerAddress(seller=newSeller)
		populateSellerAddressData(newAddress, selleraddress)

		sellerbankdetails = seller["bankdetails"]
		newBankDetails = SellerBankDetails(seller=newSeller)
		populateSellerBankDetailsData(newBankDetails, sellerbankdetails)
		
		sellerdetails = seller["details"]
		newSellerDetails = SellerDetails(seller = newSeller)
		populateSellerDetailsData(newSellerDetails, sellerdetails)
		
		newSellerDetails.save()
		newAddress.save()
		newBankDetails.save()

	except Exception as e:
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"seller" : serialize_seller(newSeller)})

def update_seller(request):
	try:
		requestbody = request.body.decode("utf-8")
		seller = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(seller) or not "sellerID" in seller or not seller["sellerID"]!=None:
		return customResponse("4XX", {"error": "Id for seller not sent"})

	sellerPtr = Seller.objects.filter(id=int(seller["sellerID"])).select_related('sellerdetails')

	if len(sellerPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for seller sent"})

	sellerPtr = sellerPtr[0]

	detailsPresent = 1
	detailsSent = 0
	addressSent = 0
	bankdetailsSent = 0

	if not validateSellerData(seller, sellerPtr, 0):
		return customResponse("4XX", {"error": "Invalid data for seller sent"})

	try:
		populateSellerData(sellerPtr, seller)
		
		if "details" in seller and seller["details"]!=None:
			detailsSent = 1
			sellerdetails = seller["details"]
			if hasattr(sellerPtr, "sellerdetails"):
				validateSellerDetailsData(sellerdetails, sellerPtr.sellerdetails)
				populateSellerDetailsData(sellerPtr.sellerdetails, sellerdetails)
			else:
				detailsPresent = 0
				validateSellerDetailsData(sellerdetails, SellerDetails())
				newSellerDetails = SellerDetails(seller = sellerPtr)
				populateSellerDetailsData(newSellerDetails, sellerdetails)

		if "address" in seller and seller["address"]!=None:
			addressSent = 1
			selleraddress = seller["address"]
			if not "addressID" in selleraddress or not selleraddress["addressID"]:
				return customResponse("4XX", {"error": "Address id not sent"})
			sellerAddressPtr = SellerAddress.objects.filter(id = int(selleraddress["addressID"]))

			if len(sellerAddressPtr) == 0:
				return customResponse("4XX", {"error": "Invalid address id sent"})

			sellerAddressPtr = sellerAddressPtr[0]
			validateSellerAddressData(selleraddress, sellerAddressPtr)
			populateSellerAddressData(sellerAddressPtr, selleraddress)
			

		if "bankdetails" in seller and seller["bankdetails"]!=None:
			bankdetailsSent = 1
			sellerbankdetails = seller["bankdetails"]
			if not "bankdetailsID" in sellerbankdetails or not sellerbankdetails["bankdetailsID"]:
				return customResponse("4XX", {"error": "Bank details id not sent"})
			sellerBankDetailsPtr = SellerBankDetails.objects.filter(id = int(sellerbankdetails["bankdetailsID"]))

			if len(sellerBankDetailsPtr) == 0:
				return customResponse("4XX", {"error": "Invalid bankdetails id sent"})

			sellerBankDetailsPtr = sellerBankDetailsPtr[0]
			validateSellerBankdetailsData(sellerbankdetails, sellerBankDetailsPtr)
			populateSellerBankDetailsData(sellerBankDetailsPtr,sellerbankdetails)

		sellerPtr.save()
		if detailsSent == 1 and detailsPresent == 1:
			sellerPtr.sellerdetails.save()
		if detailsPresent == 0:
			newSellerDetails.save()
		if addressSent == 1:
			sellerAddressPtr.save()
		if bankdetailsSent == 1:
			sellerBankDetailsPtr.save()

	except Exception as e:
		closeDBConnection()
		return customResponse("4XX", {"error": "could not update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"seller": serialize_seller(sellerPtr)})

def delete_seller(request):
	try:
		requestbody = request.body.decode("utf-8")
		seller = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(seller) or not "sellerID" in seller or not seller["sellerID"]:
		return customResponse("4XX", {"error": "Id for seller not sent"})

	sellerPtr = Seller.objects.filter(id=int(seller["sellerID"]))

	if len(sellerPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for seller sent"})

	sellerPtr = sellerPtr[0]

	try:
		sellerPtr.delete_status = True
		sellerPtr.save()
	except Exception as e:
		closeDBConnection()
		return customResponse("4XX", {"error": "could not delete"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"seller": "seller deleted"})

