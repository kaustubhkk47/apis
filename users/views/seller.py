from scripts.utils import *
import json
from ..models.seller import *
from ..serializers.seller import parse_seller, serialize_seller

from leads.models.sellerLeads import SellerLeads



def get_seller_details(request,sellersArr=[], isSeller=0,internalusersArr=[],isInternalUser=0):
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

	if sellerEmailExists(seller["email"]):
		return customResponse("4XX", {"error": "seller email already exists"})

	if sellerMobileNumberExists(seller["mobile_number"]):
		return customResponse("4XX", {"error": "seller phone number already exists"})

	if not "address" in seller or seller["address"]==None:
		seller["address"] = {}

	validateSellerAddressData(seller["address"], SellerAddress())

	if not "bank_details" in seller or seller["bank_details"]==None:
		seller["bank_details"] = {}

	validateSellerBankdetailsData(seller["bank_details"], SellerBankDetails())

	if not "details" in seller or seller["details"]==None:
			seller["details"] = {}

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
		populateSellerDetailsData(newSellerDetails, sellerdetails)
		
		newSellerDetails.save()
		newAddress.save()
		newBankDetails.save()

		sellerLeadsQuerySet = SellerLeads.objects.filter(email = newSeller.email)

		for sellerLead in sellerLeadsQuerySet:
			sellerLead.status = 1
			sellerLead.save()

	except Exception as e:
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		
		seller_email = str(newSeller.email)
		seller_password = str(newSeller.password)
		mail_template_file = "seller/registration_success.html"
		mail_dict = {"email":seller_email,"password":seller_password}
		subject = str(newSeller.name) + " congratulations on your successful registration as a seller"
		to = [seller_email]
		from_email = "Wholdus Info <info@wholdus.com>"
		attachment = "/home/probzip/webapps/wholdus_website/build/files/SellerTNC.pdf"

		create_email(mail_template_file,mail_dict,subject,from_email,to,attachment)		

		return customResponse("2XX", {"seller" : serialize_seller(newSeller)})

def update_seller(request):
	try:
		requestbody = request.body.decode("utf-8")
		seller = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(seller) or not "sellerID" in seller or seller["sellerID"]==None:
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
			

		if "bank_details" in seller and seller["bank_details"]!=None:
			bankdetailsSent = 1
			sellerbankdetails = seller["bank_details"]
			if not "bank_detailsID" in sellerbankdetails or not sellerbankdetails["bank_detailsID"]:
				return customResponse("4XX", {"error": "Bank details id not sent"})
			sellerBankDetailsPtr = SellerBankDetails.objects.filter(id = int(sellerbankdetails["bank_detailsID"]))

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