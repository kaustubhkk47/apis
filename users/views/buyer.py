from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string
import json

from ..models.buyer import Buyer, BuyerAddress, BuyerDetails
from ..serializers.buyer import serialize_buyer


def get_buyer_details(request,buyersArr=[]):
	try:
		if len(buyersArr)==0:
			buyers = Buyer.objects.all().select_related('buyerdetails')
			closeDBConnection()
		else:
			buyers = Buyer.objects.filter(id__in=buyersArr).select_related('buyerdetails')
			closeDBConnection()

		response = {
			"buyers" : parse_buyer(buyers)
		}

		return customResponse("2XX", response)
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid request"})

def post_new_buyer(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer = json.loads(requestbody)
		buyer = convert_keys_to_string(buyer)
	except Exception as e:
		print e
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer):
		return customResponse("4XX", {"error": "Invalid data for buyer sent"})

	validateBuyerData(buyer)

	try:
		newBuyer = Buyer.objects.create(name = buyer["name"], company_name = buyer["company_name"],
			mobile_number = buyer["mobile_number"], email = buyer["email"], password = buyer["password"],
			alternate_phone_number = buyer["alternate_phone_number"], mobile_verification = bool(buyer["mobile_verification"]),
			email_verification=bool(buyer["email_verification"]),gender = buyer["gender"])

		if "address" in buyer and buyer["address"]:
			validateBuyerAddressData(buyer["address"])
			buyeraddress = buyer["address"]
			newAddress = BuyerAddress.objects.create(buyer=newBuyer, address = buyeraddress["address"],
				landmark = buyeraddress["landmark"], city = buyeraddress["city"], state = buyeraddress["state"],
				country = buyeraddress["country"], contact_number = buyeraddress["contact_number"],
				pincode = buyeraddress["pincode"])

		if not "details" in buyer or not buyer["details"]:
			buyer_details = {}
			buyer["details"] = buyer_details

		validateBuyerDetailsData(buyer["details"])

		buyerdetails = buyer["details"]
		newBuyerDetails = BuyerDetails.objects.create(buyer = newBuyer, vat_tin = buyerdetails["vat_tin"],
			cst = buyerdetails["cst"], buyer_interest = buyerdetails["buyer_interest"],
			customer_type = buyerdetails["customer_type"], buying_capacity = buyerdetails["buying_capacity"],
			buys_from = buyerdetails["buys_from"], purchasing_states = buyerdetails["purchasing_states"])

	except Exception as e:
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer" : serialize_buyer(newBuyer)})
	
def validateBuyerData(buyer):

	if not "name" in buyer or not buyer["name"]:
		buyer["name"] = ""
	if not "company_name" in buyer or not buyer["company_name"]:
		buyer["company_name"] = ""
	if not "mobile_number" in buyer or not buyer["mobile_number"]:
		buyer["mobile_number"] = ""
	if not "email" in buyer or not buyer["email"]:
		buyer["email"] = ""
	if not "password" in buyer or not buyer["password"]:
		buyer["password"] = ""
	if not "alternate_phone_number" in buyer or not buyer["alternate_phone_number"]:
		buyer["alternate_phone_number"] = ""
	if not "mobile_verification" in buyer or not buyer["mobile_verification"]:
		buyer["mobile_verification"] = 0
	if not "email_verification" in buyer or not buyer["email_verification"]:
		buyer["email_verification"] = 0
	if not "gender" in buyer or not buyer["gender"]:
		buyer["gender"] = ""
	

def validateBuyerDetailsData(buyerdetails):

	if not "vat_tin" in buyerdetails or not buyerdetails["vat_tin"]:
		buyerdetails["vat_tin"] = ""
	if not "cst" in buyerdetails or not buyerdetails["cst"]:
		buyerdetails["cst"] = ""
	if not "buyer_interest" in buyerdetails or not buyerdetails["buyer_interest"]:
		buyerdetails["buyer_interest"] = ""
	if not "customer_type" in buyerdetails or not buyerdetails["customer_type"]:
		buyerdetails["customer_type"] = ""
	if not "buying_capacity" in buyerdetails or not buyerdetails["buying_capacity"]:
		buyerdetails["buying_capacity"] = ""
	if not "buys_from" in buyerdetails or not buyerdetails["buys_from"]:
		buyerdetails["buys_from"] = ""
	if not "purchasing_states" in buyerdetails or not buyerdetails["purchasing_states"]:
		buyerdetails["purchasing_states"] = ""


def validateBuyerAddressData(buyeraddress):

	if not "address" in buyeraddress or not buyeraddress["address"]:
		buyeraddress["address"] = ""
	if not "landmark" in buyeraddress or not buyeraddress["landmark"]:
		buyeraddress["landmark"] = ""
	if not "city" in buyeraddress or not buyeraddress["city"]:
		buyeraddress["city"] = ""
	if not "state" in buyeraddress or not buyeraddress["state"]:
		buyeraddress["state"] = ""
	if not "country" in buyeraddress or not buyeraddress["country"]:
		buyeraddress["country"] = ""
	if not "contact_number" in buyeraddress or not buyeraddress["contact_number"]:
		buyeraddress["contact_number"] = ""
	if not "pincode" in buyeraddress or not buyeraddress["pincode"]:
		buyeraddress["pincode"] = ""