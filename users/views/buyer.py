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
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer) or not validateBuyerData(buyer, Buyer()):
		return customResponse("4XX", {"error": "Invalid data for buyer sent"})

	try:
		newBuyer = Buyer.objects.create(name = buyer["name"], company_name = buyer["company_name"],
			mobile_number = buyer["mobile_number"], email = buyer["email"], password = buyer["password"],
			alternate_phone_number = buyer["alternate_phone_number"], mobile_verification = bool(buyer["mobile_verification"]),
			email_verification=bool(buyer["email_verification"]),gender = buyer["gender"])

		if "address" in buyer and buyer["address"]:
			validateBuyerAddressData(buyer["address"], BuyerAddress())
			buyeraddress = buyer["address"]
			newAddress = BuyerAddress.objects.create(buyer=newBuyer, address = buyeraddress["address"],
				landmark = buyeraddress["landmark"], city = buyeraddress["city"], state = buyeraddress["state"],
				country = buyeraddress["country"], contact_number = buyeraddress["contact_number"],
				pincode = buyeraddress["pincode"])

		if not "details" in buyer or not buyer["details"]:
			buyer_details = {}
			buyer["details"] = buyer_details

		validateBuyerDetailsData(buyer["details"], BuyerDetails())

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

def update_buyer(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer) or not "buyerID" in buyer or not buyer["buyerID"]:
		return customResponse("4XX", {"error": "Id for buyer not sent"})

	buyerPtr = Buyer.objects.filter(id=int(buyer["buyerID"])).select_related('buyerdetails')

	if len(buyerPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for buyer sent"})

	buyerPtr = buyerPtr[0]

	detailsPresent = 1
	addressSent = 0

	if not validateBuyerData(buyer, buyerPtr):
		return customResponse("4XX", {"error": "Invalid data for buyer sent"})

	try:
		buyerPtr.name = buyer["name"]
		buyerPtr.company_name = buyer["company_name"]
		buyerPtr.mobile_number = buyer["mobile_number"]
		buyerPtr.email = buyer["email"]
		buyerPtr.password = buyer["password"]
		buyerPtr.alternate_phone_number = buyer["alternate_phone_number"]
		buyerPtr.mobile_verification = bool(buyer["mobile_verification"])
		buyerPtr.email_verification = bool(buyer["email_verification"])
		buyerPtr.gender = buyer["gender"]

		if "details" in buyer and buyer["details"]:
			buyerdetails = buyer["details"]
			if hasattr(buyerPtr, "buyerdetails"):
				validateBuyerDetailsData(buyerdetails, buyerPtr.buyerdetails)
				buyerPtr.buyerdetails.cst = buyerdetails["cst"]
				buyerPtr.buyerdetails.buyer_interest = buyerdetails["buyer_interest"]
				buyerPtr.buyerdetails.customer_type = buyerdetails["customer_type"]
				buyerPtr.buyerdetails.buying_capacity = buyerdetails["buying_capacity"]
				buyerPtr.buyerdetails.buys_from = buyerdetails["buys_from"]
				buyerPtr.buyerdetails.purchasing_states = buyerdetails["purchasing_states"]
				buyerPtr.buyerdetails.vat_tin = buyerdetails["vat_tin"]

			else:
				detailsPresent = 0
				validateBuyerDetailsData(buyerdetails, BuyerDetails())
				newBuyerDetails = BuyerDetails(buyer = buyerPtr, vat_tin = buyerdetails["vat_tin"],
					cst = buyerdetails["cst"], buyer_interest = buyerdetails["buyer_interest"],
					customer_type = buyerdetails["customer_type"], buying_capacity = buyerdetails["buying_capacity"],
					buys_from = buyerdetails["buys_from"], purchasing_states = buyerdetails["purchasing_states"])

		if "address" in buyer and buyer["address"]:
			addressSent = 1
			buyeraddress = buyer["address"]
			if not "addressID" in buyeraddress or not buyeraddress["addressID"]:
				return customResponse("4XX", {"error": "Address id not sent"})
			buyerAddressPtr = BuyerAddress.objects.filter(id = buyeraddress["addressID"])

			if len(buyerAddressPtr) == 0:
				return customResponse("4XX", {"error": "Invalid address id sent"})

			buyerAddressPtr = buyerAddressPtr[0]

			validateBuyerAddressData(buyeraddress, buyerAddressPtr)

			buyerAddressPtr.address = buyeraddress["address"]
			buyerAddressPtr.landmark = buyeraddress["landmark"]
			buyerAddressPtr.city = buyeraddress["city"]
			buyerAddressPtr.state = buyeraddress["state"]
			buyerAddressPtr.country = buyeraddress["country"]
			buyerAddressPtr.contact_number = buyeraddress["contact_number"]
			buyerAddressPtr.pincode = buyeraddress["pincode"]

		buyerPtr.save()
		if detailsPresent == 0:
			newBuyerDetails.save()
		if addressSent == 1:
			buyerAddressPtr.save()

	except Exception as e:
		closeDBConnection()
		return customResponse("4XX", {"error": "could not update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer": serialize_buyer(buyerPtr)})


def validateBuyerData(buyer, oldbuyer):

	if not "name" in buyer or not buyer["name"]:
		buyer["name"] = oldbuyer.name
	if not "company_name" in buyer or not buyer["company_name"]:
		buyer["company_name"] = oldbuyer.company_name
	if not "mobile_number" in buyer or not buyer["mobile_number"]:
		buyer["mobile_number"] = oldbuyer.mobile_number
	if not "email" in buyer or not buyer["email"]:
		buyer["email"] = oldbuyer.email
	if not "password" in buyer or not buyer["password"]:
		buyer["password"] = oldbuyer.password
	if not "alternate_phone_number" in buyer or not buyer["alternate_phone_number"]:
		buyer["alternate_phone_number"] = oldbuyer.alternate_phone_number
	if not "mobile_verification" in buyer or not buyer["mobile_verification"]:
		buyer["mobile_verification"] = oldbuyer.mobile_verification
	if not "email_verification" in buyer or not buyer["email_verification"]:
		buyer["email_verification"] = oldbuyer.email_verification
	if not "gender" in buyer or not buyer["gender"]:
		buyer["gender"] = oldbuyer.gender

	return True


	
def validateBuyerDetailsData(buyerdetails, oldbuyerdetails):

	if not "vat_tin" in buyerdetails or not buyerdetails["vat_tin"]:
		buyerdetails["vat_tin"] = oldbuyerdetails.vat_tin
	if not "cst" in buyerdetails or not buyerdetails["cst"]:
		buyerdetails["cst"] = oldbuyerdetails.cst
	if not "buyer_interest" in buyerdetails or not buyerdetails["buyer_interest"]:
		buyerdetails["buyer_interest"] = oldbuyerdetails.buyer_interest
	if not "customer_type" in buyerdetails or not buyerdetails["customer_type"]:
		buyerdetails["customer_type"] = oldbuyerdetails.customer_type
	if not "buying_capacity" in buyerdetails or not buyerdetails["buying_capacity"]:
		buyerdetails["buying_capacity"] = oldbuyerdetails.buying_capacity
	if not "buys_from" in buyerdetails or not buyerdetails["buys_from"]:
		buyerdetails["buys_from"] = oldbuyerdetails.buys_from
	if not "purchasing_states" in buyerdetails or not buyerdetails["purchasing_states"]:
		buyerdetails["purchasing_states"] = oldbuyerdetails.purchasing_states 


def validateBuyerAddressData(buyeraddress, oldbuyeraddress):

	if not "address" in buyeraddress or not buyeraddress["address"]:
		buyeraddress["address"] = oldbuyeraddress.address
	if not "landmark" in buyeraddress or not buyeraddress["landmark"]:
		buyeraddress["landmark"] = oldbuyeraddress.landmark
	if not "city" in buyeraddress or not buyeraddress["city"]:
		buyeraddress["city"] = oldbuyeraddress.city
	if not "state" in buyeraddress or not buyeraddress["state"]:
		buyeraddress["state"] = oldbuyeraddress.state
	if not "country" in buyeraddress or not buyeraddress["country"]:
		buyeraddress["country"] = oldbuyeraddress.country
	if not "contact_number" in buyeraddress or not buyeraddress["contact_number"]:
		buyeraddress["contact_number"] = oldbuyeraddress.contact_number
	if not "pincode" in buyeraddress or not buyeraddress["pincode"]:
		buyeraddress["pincode"] = oldbuyeraddress.pincode