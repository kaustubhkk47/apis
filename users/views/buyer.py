from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string
import json

from ..models.buyer import Buyer, BuyerAddress, BuyerDetails, validateBuyerData, validateBuyerDetailsData, validateBuyerAddressData
from ..serializers.buyer import serialize_buyer, parse_buyer


def get_buyer_details(request,buyersArr=[]):
	try:
		if len(buyersArr)==0:
			buyers = Buyer.objects.filter(delete_status=False).select_related('buyerdetails')
			closeDBConnection()
		else:
			buyers = Buyer.objects.filter(delete_status=False,id__in=buyersArr).select_related('buyerdetails')
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

	if not len(buyer) or not validateBuyerData(buyer, Buyer(), 1):
		return customResponse("4XX", {"error": "Invalid data for buyer sent"})

	if not "address" in buyer or not buyer["address"]:
		buyer["address"] = {}
		
	validateBuyerAddressData(buyer["address"], BuyerAddress())

	if not "details" in buyer or not buyer["details"]:
		buyer["details"] = {}

	try:

		validateBuyerDetailsData(buyer["details"], BuyerDetails())

		newBuyer = Buyer(name = buyer["name"], company_name = buyer["company_name"],
			mobile_number = buyer["mobile_number"], email = buyer["email"], password = buyer["password"],
			alternate_phone_number = buyer["alternate_phone_number"], mobile_verification = bool(buyer["mobile_verification"]),
			email_verification=bool(buyer["email_verification"]),gender = buyer["gender"])

		newBuyer.save()

		buyeraddress = buyer["address"]
		newAddress = BuyerAddress(buyer=newBuyer, address = buyeraddress["address"],
				landmark = buyeraddress["landmark"], city = buyeraddress["city"], state = buyeraddress["state"],
				country = buyeraddress["country"], contact_number = buyeraddress["contact_number"],
				pincode = buyeraddress["pincode"])

		buyerdetails = buyer["details"]
		newBuyerDetails = BuyerDetails(buyer = newBuyer, vat_tin = buyerdetails["vat_tin"],
			cst = buyerdetails["cst"], buyer_interest = buyerdetails["buyer_interest"],
			customer_type = buyerdetails["customer_type"], buying_capacity = buyerdetails["buying_capacity"],
			buys_from = buyerdetails["buys_from"], purchasing_states = buyerdetails["purchasing_states"])
		
		newBuyerDetails.save()
		newAddress.save()
		 
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
	detailsSent = 0
	addressSent = 0

	if not validateBuyerData(buyer, buyerPtr, 0):
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
			detailsSent = 1
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
			buyerAddressPtr = BuyerAddress.objects.filter(id = int(buyeraddress["addressID"]))

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
		if detailsSent == 1 and detailsPresent == 1:
			buyerPtr.buyerdetails.save()
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

def delete_buyer(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyer = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyer) or not "buyerID" in buyer or not buyer["buyerID"]:
		return customResponse("4XX", {"error": "Id for buyer not sent"})

	buyerPtr = Buyer.objects.filter(id=int(buyer["buyerID"]))

	if len(buyerPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for buyer sent"})

	buyerPtr = buyerPtr[0]

	try:
		buyerPtr.delete_status = True
		buyerPtr.save()
	except Exception as e:
		closeDBConnection()
		return customResponse("4XX", {"error": "could not delete"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer": "buyer deleted"})
