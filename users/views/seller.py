from scripts.utils import *
import json
from ..models.seller import *
from ..serializers.seller import parse_seller, serialize_seller
from ..models.businessType import BusinessType
from catalog.models.product import Product
from leads.models.sellerLeads import SellerLeads

import logging
log = logging.getLogger("django")

from django.utils import timezone

def get_seller_details(request,parameters):
	try:
		if "isSeller" in parameters and parameters["isSeller"] == 1:
			parameters["seller_show_online"] = 1
			
		sellers = filterSeller(parameters)

		response = {
			"sellers" : parse_seller(sellers, parameters)
		}

		closeDBConnection()

		return customResponse(200, response)
	except Exception as e:
		log.critical(e)
		return customResponse(500)

def post_new_seller(request):
	try:
		requestbody = request.body.decode("utf-8")
		seller = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(seller) or not validateSellerData(seller, Seller(), 1):
		return customResponse(400, error_code=5,  error_details= "Invalid data for seller sent")

	if sellerEmailExists(seller["email"]):
		return customResponse(400, error_code=6,  error_details= "seller email already exists")

	if sellerMobileNumberExists(seller["mobile_number"]):
		return customResponse(400, error_code=6,  error_details= "seller phone number already exists")

	if not "address" in seller or seller["address"]==None:
		seller["address"] = {}

	validateSellerAddressData(seller["address"], SellerAddress())

	if not "bank_details" in seller or seller["bank_details"]==None:
		seller["bank_details"] = {}

	validateSellerBankdetailsData(seller["bank_details"], SellerBankDetails())

	if not "details" in seller or seller["details"]==None:
		seller["details"] = {
			"sellertypeID":1
		}

	validateSellerDetailsData(seller["details"], SellerDetails())

	try:
		newSeller = Seller()
		populateSellerData(newSeller, seller)

		newSeller.save()

		selleraddress = seller["address"]
		newAddress = SellerAddress(seller=newSeller)
		populateSellerAddressData(newAddress, selleraddress)

		sellerbankdetails = seller["bank_details"]
		newBankDetails = SellerBankDetails(seller=newSeller)
		populateSellerBankDetailsData(newBankDetails, sellerbankdetails)
		
		sellerdetails = seller["details"]
		newSellerDetails = SellerDetails(seller = newSeller)
		if "sellertypeID" in seller["details"] and validate_integer(seller["details"]["sellertypeID"]):
			businessTypePtr = BusinessType.objects.filter(id=int(seller["details"]["sellertypeID"]), can_be_seller=True)
			if len(businessTypePtr) > 0:
				businessTypePtr = businessTypePtr[0]
				newSellerDetails.seller_type = businessTypePtr
		populateSellerDetailsData(newSellerDetails, sellerdetails)
		
		newSellerDetails.save()
		newAddress.save()
		newBankDetails.save()

		newSellerAddressHistory = SellerAddressHistory()
		newSellerAddressHistory.populateFromSellerAddress(newAddress)
		newSellerAddressHistory.save()

		sellerLeadsQuerySet = SellerLeads.objects.filter(email = newSeller.email)

		for sellerLead in sellerLeadsQuerySet:
			sellerLead.status = 1
			sellerLead.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		
		newSeller.send_registration_mail()

		return customResponse(200, {"seller" : serialize_seller(newSeller)})

def update_seller(request):
	try:
		requestbody = request.body.decode("utf-8")
		seller = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(seller) or not "sellerID" in seller or not validate_integer(seller["sellerID"]):
		return customResponse(400, error_code=5,  error_details="Id for seller not sent")

	sellerPtr = Seller.objects.filter(id=int(seller["sellerID"]), delete_status=False).select_related('sellerdetails')

	if len(sellerPtr) == 0:
		return customResponse(400, error_code=6,  error_details="Invalid id for seller sent")

	sellerPtr = sellerPtr[0]

	detailsPresent = 1
	detailsSent = 0
	addressSent = 0
	bankdetailsSent = 0

	if not validateSellerData(seller, sellerPtr, 0):
		return customResponse(400, error_code=5,  error_details="Invalid data for seller sent")

	try:
		if sellerPtr.show_online != int(seller["show_online"]):
			Product.objects.filter(seller_id = sellerPtr.id).update(show_online= int(seller["show_online"]), updated_at=timezone.now())

		populateSellerData(sellerPtr, seller)
		
		if "details" in seller and seller["details"]!=None:
			detailsSent = 1
			sellerdetails = seller["details"]
			if hasattr(sellerPtr, "sellerdetails"):
				validateSellerDetailsData(sellerdetails, sellerPtr.sellerdetails)
				populateSellerDetailsData(sellerPtr.sellerdetails, sellerdetails)
				if "sellertypeID" in seller["details"] and validate_integer(seller["details"]["sellertypeID"]):
					businessTypePtr = BusinessType.objects.filter(id=int(seller["details"]["sellertypeID"]), can_be_seller=True)
					if len(businessTypePtr) > 0:
						businessTypePtr = businessTypePtr[0]
						sellerPtr.sellerdetails.seller_type = businessTypePtr
			else:
				detailsPresent = 0
				validateSellerDetailsData(sellerdetails, SellerDetails())
				newSellerDetails = SellerDetails(seller = sellerPtr)
				if "sellertypeID" in seller["details"] and validate_integer(seller["details"]["sellertypeID"]):
					businessTypePtr = BusinessType.objects.filter(id=int(seller["details"]["sellertypeID"]), can_be_seller=True)
					if len(businessTypePtr) > 0:
						businessTypePtr = businessTypePtr[0]
						newSellerDetails.seller_type = businessTypePtr
				populateSellerDetailsData(newSellerDetails, sellerdetails)

		if "address" in seller and seller["address"]!=None:
			addressSent = 1
			selleraddress = seller["address"]
			if not "addressID" in selleraddress or not validate_integer(selleraddress["addressID"]):
				return customResponse(400, error_code=5,  error_details="Address id not sent")
			sellerAddressPtr = SellerAddress.objects.filter(id = int(selleraddress["addressID"]))

			if len(sellerAddressPtr) == 0:
				return customResponse(400, error_code=6,  error_details="Invalid address id sent")

			sellerAddressPtr = sellerAddressPtr[0]

			if(sellerAddressPtr.seller_id != sellerPtr.id):
				return customResponse(400, error_code=6,  error_details="Address id for incorrect seller sent")

			validateSellerAddressData(selleraddress, sellerAddressPtr)
			populateSellerAddressData(sellerAddressPtr, selleraddress)
			

		if "bank_details" in seller and seller["bank_details"]!=None:
			bankdetailsSent = 1
			sellerbankdetails = seller["bank_details"]
			if not "bank_detailsID" in sellerbankdetails or not validate_integer(sellerbankdetails["bank_detailsID"]):
				return customResponse(400, error_code=5,  error_details= "Bank details id not sent")
			sellerBankDetailsPtr = SellerBankDetails.objects.filter(id = int(sellerbankdetails["bank_detailsID"]))

			if len(sellerBankDetailsPtr) == 0:
				return customResponse(400, error_code=6,  error_details="Invalid bankdetails id sent")

			sellerBankDetailsPtr = sellerBankDetailsPtr[0]

			if(sellerBankDetailsPtr.seller_id != sellerPtr.id):
				return customResponse(400, error_code=6,  error_details="Bank details id for incorrect seller sent")

			validateSellerBankdetailsData(sellerbankdetails, sellerBankDetailsPtr)
			populateSellerBankDetailsData(sellerBankDetailsPtr,sellerbankdetails)

		sellerPtr.save()
		if detailsSent == 1 and detailsPresent == 1:
			sellerPtr.sellerdetails.save()
		if detailsPresent == 0:
			newSellerDetails.save()
		if addressSent == 1:
			sellerAddressPtr.save()
			newSellerAddressHistory = SellerAddressHistory()
			newSellerAddressHistory.populateFromSellerAddress(sellerAddressPtr)
			newSellerAddressHistory.save()
		if bankdetailsSent == 1:
			sellerBankDetailsPtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"seller": serialize_seller(sellerPtr)})

def delete_seller(request):
	try:
		requestbody = request.body.decode("utf-8")
		seller = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(seller) or not "sellerID" in seller or not validate_integer(seller["sellerID"]):
		return customResponse(400, error_code=5,  error_details= "Id for seller not sent")

	sellerPtr = Seller.objects.filter(id=int(seller["sellerID"]), delete_status=False)

	if len(sellerPtr) == 0:
		return customResponse(400, error_code=5,  error_details= "Invalid id for seller sent")

	sellerPtr = sellerPtr[0]

	try:
		sellerPtr.delete_status = True
		Product.objects.filter(seller_id = sellerPtr.id).update(delete_status=True, updated_at=timezone.now())
		sellerPtr.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"seller": "seller deleted"})