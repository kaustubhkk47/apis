from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string, validate_date_time
import json
from ..models.seller import Seller, SellerAddress, SellerBankDetails, SellerDetails, validateSellerData, validateSellerAddressData, validateSellerDetailsData, validateSellerBankdetailsData
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

	if not "address" in seller or not seller["address"]:
		seller["address"] = {}

	validateSellerAddressData(seller["address"], SellerAddress())

	if not "bankdetails" in seller or not seller["bankdetails"]:
		seller["bankdetails"] = {}

	validateSellerBankdetailsData(seller["bankdetails"], SellerBankDetails())

	if not "details" in seller or not seller["details"]:
			seller["details"] = {}

	validateSellerDetailsData(seller["details"], SellerDetails())

	try:
		newSeller = Seller(name = seller["name"], company_name = seller["company_name"],
			mobile_number = seller["mobile_number"], email = seller["email"], password = seller["password"],
			alternate_phone_number = seller["alternate_phone_number"], mobile_verification = bool(seller["mobile_verification"]),
			email_verification=bool(seller["email_verification"]))

		newSeller.save()

		selleraddress = seller["address"]
		newAddress = SellerAddress(seller=newSeller, address = selleraddress["address"],
				landmark = selleraddress["landmark"], city = selleraddress["city"], state = selleraddress["state"],
				country = selleraddress["country"], contact_number = selleraddress["contact_number"],
				pincode = selleraddress["pincode"])

		sellerbankdetails = seller["bankdetails"]
		newBankDetails = SellerBankDetails(seller=newSeller, account_holders_name = sellerbankdetails["account_holders_name"],
				account_number = sellerbankdetails["account_number"], ifsc = sellerbankdetails["ifsc"], bank_name = sellerbankdetails["bank_name"],
				branch = sellerbankdetails["branch"], branch_city = sellerbankdetails["branch_city"],
				branch_pincode = sellerbankdetails["branch_pincode"])
		
		sellerdetails = seller["details"]
		newSellerDetails = SellerDetails(seller = newSeller, vat_tin = sellerdetails["vat_tin"],
			cst = sellerdetails["cst"], pan = sellerdetails["pan"],
			name_on_pan = sellerdetails["name_on_pan"], dob_on_pan = sellerdetails["dob_on_pan"],
			pan_verification = sellerdetails["pan_verification"], tin_verification = sellerdetails["tin_verification"])
		
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
		print e
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(seller) or not "sellerID" in seller or not seller["sellerID"]:
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
		sellerPtr.name = seller["name"]
		sellerPtr.company_name = seller["company_name"]
		sellerPtr.mobile_number = seller["mobile_number"]
		sellerPtr.email = seller["email"]
		sellerPtr.password = seller["password"]
		sellerPtr.alternate_phone_number = seller["alternate_phone_number"]
		sellerPtr.mobile_verification = bool(seller["mobile_verification"])
		sellerPtr.email_verification = bool(seller["email_verification"])

		if "details" in seller and seller["details"]:
			detailsSent = 1
			sellerdetails = seller["details"]
			if hasattr(sellerPtr, "sellerdetails"):
				validateSellerDetailsData(sellerdetails, sellerPtr.sellerdetails)
				sellerPtr.sellerdetails.cst = sellerdetails["cst"]
				sellerPtr.sellerdetails.pan = sellerdetails["pan"]
				sellerPtr.sellerdetails.name_on_pan = sellerdetails["name_on_pan"]
				sellerPtr.sellerdetails.dob_on_pan = sellerdetails["dob_on_pan"]
				sellerPtr.sellerdetails.pan_verification = bool(sellerdetails["pan_verification"])
				sellerPtr.sellerdetails.tin_verification = bool(sellerdetails["tin_verification"])
				sellerPtr.sellerdetails.vat_tin = sellerdetails["vat_tin"]

			else:
				detailsPresent = 0
				validateSellerDetailsData(sellerdetails, SellerDetails())
				newSellerDetails = SellerDetails(seller = sellerPtr, vat_tin = sellerdetails["vat_tin"],
					cst = sellerdetails["cst"], pan = sellerdetails["pan"],
					name_on_pan = sellerdetails["name_on_pan"], dob_on_pan = sellerdetails["dob_on_pan"],
					pan_verification = sellerdetails["pan_verification"], tin_verification = sellerdetails["tin_verification"])

		if "address" in seller and seller["address"]:
			addressSent = 1
			selleraddress = seller["address"]
			if not "addressID" in selleraddress or not selleraddress["addressID"]:
				return customResponse("4XX", {"error": "Address id not sent"})
			sellerAddressPtr = SellerAddress.objects.filter(id = selleraddress["addressID"])

			if len(sellerAddressPtr) == 0:
				return customResponse("4XX", {"error": "Invalid address id sent"})

			sellerAddressPtr = sellerAddressPtr[0]

			validateSellerAddressData(selleraddress, sellerAddressPtr)

			sellerAddressPtr.address = selleraddress["address"]
			sellerAddressPtr.landmark = selleraddress["landmark"]
			sellerAddressPtr.city = selleraddress["city"]
			sellerAddressPtr.state = selleraddress["state"]
			sellerAddressPtr.country = selleraddress["country"]
			sellerAddressPtr.contact_number = selleraddress["contact_number"]
			sellerAddressPtr.pincode = selleraddress["pincode"]

		if "bankdetails" in seller and seller["bankdetails"]:
			bankdetailsSent = 1
			sellerbankdetails = seller["bankdetails"]
			if not "bankdetailsID" in sellerbankdetails or not sellerbankdetails["bankdetailsID"]:
				return customResponse("4XX", {"error": "Bank details id not sent"})
			sellerBankDetailsPtr = SellerBankDetails.objects.filter(id = sellerbankdetails["bankdetailsID"])

			if len(sellerBankDetailsPtr) == 0:
				return customResponse("4XX", {"error": "Invalid bankdetails id sent"})

			sellerBankDetailsPtr = sellerBankDetailsPtr[0]

			validateSellerBankdetailsData(sellerbankdetails, sellerBankDetailsPtr)

			sellerBankDetailsPtr.account_holders_name = sellerbankdetails["account_holders_name"]
			sellerBankDetailsPtr.account_number = sellerbankdetails["account_number"]
			sellerBankDetailsPtr.ifsc = sellerbankdetails["ifsc"]
			sellerBankDetailsPtr.bank_name = sellerbankdetails["bank_name"]
			sellerBankDetailsPtr.branch = sellerbankdetails["branch"]
			sellerBankDetailsPtr.branch_city = sellerbankdetails["branch_city"]
			sellerBankDetailsPtr.branch_pincode = sellerbankdetails["branch_pincode"]

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

