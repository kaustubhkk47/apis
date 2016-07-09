from ..models.buyer import Buyer, BuyerAddress, BuyerDetails, filterBuyer, filterBuyerInterest, filterBuyerProducts
from catalog.serializers.category import serialize_categories
from catalog.serializers.product import serialize_product

def serialize_buyer(buyer_entry, parameters = {}):

	buyer = {}

	if "buyer_address_details" in parameters and parameters["buyer_address_details"] == 1:
		buyer_addresses_queryset = BuyerAddress.objects.filter(buyer_id = buyer_entry.id)
		buyer_addresses = parse_buyer_address(buyer_addresses_queryset, parameters)
		buyer["address"] = buyer_addresses

	buyer["buyerID"] = buyer_entry.id
	buyer["name"] = buyer_entry.name
	buyer["whatsapp_contact_name"] = buyer_entry.whatsapp_contact_name
	buyer["company_name"] = buyer_entry.company_name
	buyer["mobile_number"] = buyer_entry.mobile_number
	buyer["whatsapp_number"] = buyer_entry.whatsapp_number
	buyer["email"] = buyer_entry.email
	buyer["alternate_phone_number"] = buyer_entry.alternate_phone_number
	buyer["mobile_verification"] = buyer_entry.mobile_verification
	buyer["email_verification"] = buyer_entry.email_verification
	buyer["whatsapp_sharing_active"] = buyer_entry.whatsapp_sharing_active
	buyer["gender"] = buyer_entry.gender
	buyer["created_at"] = buyer_entry.created_at
	buyer["updated_at"] = buyer_entry.updated_at
	
	if "buyer_details_details" in parameters and parameters["buyer_details_details"] == 1 and hasattr(buyer_entry,'buyerdetails'):
		buyer_details = {}
		buyer_details["detailsID"] = buyer_entry.buyerdetails.id
		buyer_details["vat_tin"] = buyer_entry.buyerdetails.vat_tin
		buyer_details["cst"] = buyer_entry.buyerdetails.cst
		buyer_details["customer_type"] = buyer_entry.buyerdetails.customer_type
		buyer_details["buying_capacity"] = buyer_entry.buyerdetails.buying_capacity
		buyer_details["purchase_duration"] = buyer_entry.buyerdetails.purchase_duration

		buyer["details"] = buyer_details

	if "buyer_interest_details" in parameters and parameters["buyer_interest_details"] == 1:
	   buyerInterestQuerySet = filterBuyerInterest(parameters)
	   buyerInterestQuerySet = buyerInterestQuerySet.filter(buyer_id = buyer_entry.id)
	   buyer["buyer_interests"] = parse_buyer_interest(buyerInterestQuerySet,parameters)

	if "buyer_product_details" in parameters and parameters["buyer_product_details"] == 1:
		tempParameters = parameters
		tempParameters["buyer_interest_active"] = True
		tempParameters["buyer_product_delete_status"] = False
		tempParameters["buyer_product_is_active"] = True
		tempParameters["responded"] = 0
		buyerProductQuerySet = filterBuyerProducts(tempParameters)
		buyerProductQuerySet = buyerProductQuerySet.filter(buyer_id = buyer_entry.id)
		buyerProductQuerySet = buyerProductQuerySet[:parameters["buyer_product_count"]]
		buyer["buyer_products"] = parse_buyer_product(buyerProductQuerySet,parameters)

	return buyer


def parse_buyer_address(buyer_addresses_queryset, parameters = {}):

	buyer_addresses =[]

	for buyer_address in buyer_addresses_queryset:

		buyer_address_entry = serialize_buyer_address(buyer_address, parameters)
		buyer_addresses.append(buyer_address_entry)

	return buyer_addresses

def serialize_buyer_address(buyer_address, parameters = {}):
	buyer_address_entry = {
		"addressID" : buyer_address.id,
		"address" : buyer_address.address_line,
		"landmark" : buyer_address.landmark,
		"city" : buyer_address.city_name,
		"state" : buyer_address.state_name,
		"country" : buyer_address.country_name,
		"contact_number" : buyer_address.contact_number,
		"pincode" : buyer_address.pincode_number,
		"priority" : buyer_address.priority
	}
	return buyer_address_entry

def parse_buyer(buyers_queryset, parameters = {}):

	buyers = []

	for buyer in buyers_queryset:
		buyer_entry = serialize_buyer(buyer, parameters)
		buyers.append(buyer_entry)

	return buyers

def parse_buyer_shared_product_id(buyers_queryset, parameters = {}):

	buyers = []

	for buyer in buyers_queryset:
		buyer_entry = serialize_buyer_shared_product_id(buyer, parameters)
		buyers.append(buyer_entry)

	return buyers

def serialize_buyer_shared_product_id(buyer_shared_product_id_entry, parameters = {}):
	buyer_shared_product_id = {}

	buyer_shared_product_id["buyersharedproductID"] = buyer_shared_product_id_entry.id
	buyer_shared_product_id["buyerID"] = buyer_shared_product_id_entry.buyer_id
	buyer_shared_product_id["productID"] = buyer_shared_product_id_entry.productid_filter_text
	buyer_shared_product_id["created_at"] = buyer_shared_product_id_entry.created_at
	buyer_shared_product_id["updated_at"] = buyer_shared_product_id_entry.updated_at
	buyer_shared_product_id["delete_status"] = buyer_shared_product_id_entry.delete_status

	return buyer_shared_product_id


def parse_buyer_interest(buyer_interests_queryset, parameters = {}):

	buyer_interests = []

	for buyer_interest in buyer_interests_queryset:
		buyer_interest_entry = serialize_buyer_interest(buyer_interest, parameters)
		buyer_interests.append(buyer_interest_entry)

	return buyer_interests

def serialize_buyer_interest(buyer_interest_entry, parameters = {}):

	buyer_interest = {}

	buyer_interest["buyerinterestID"] = buyer_interest_entry.id
	buyer_interest["scale"] = buyer_interest_entry.scale
	buyer_interest["price_filter_applied"] = buyer_interest_entry.price_filter_applied
	buyer_interest["min_price_per_unit"] = buyer_interest_entry.min_price_per_unit
	buyer_interest["max_price_per_unit"] = buyer_interest_entry.max_price_per_unit
	buyer_interest["fabric_filter_text"] = buyer_interest_entry.fabric_filter_text
	buyer_interest["productid_filter_text"] = buyer_interest_entry.productid_filter_text
	buyer_interest["is_active"] = buyer_interest_entry.is_active
	buyer_interest["created_at"] = buyer_interest_entry.created_at
	buyer_interest["updated_at"] = buyer_interest_entry.updated_at

	buyer_interest["category"] = serialize_categories(buyer_interest_entry.category)

	return buyer_interest

def parse_buyer_product(buyer_products_queryset, parameters = {}):

	buyer_products = []

	for buyer_product in buyer_products_queryset:
		buyer_product_entry = serialize_buyer_product(buyer_product, parameters)
		buyer_products.append(buyer_product_entry)

	return buyer_products

def serialize_buyer_product(buyer_product_entry, parameters = {}):

	buyer_product = {}

	buyer_product["buyerproductID"] = buyer_product_entry.id
	if hasattr(buyer_product_entry,"buyer_interest"):
		buyer_product["buyerinterestID"] = buyer_product_entry.buyer_interest_id
	buyer_product["is_active"] = buyer_product_entry.is_active
	buyer_product["responded"] = buyer_product_entry.responded
	buyer_product["shortlisted_time"] = buyer_product_entry.shortlisted_time
	buyer_product["disliked_time"] = buyer_product_entry.disliked_time
	buyer_product["created_at"] = buyer_product_entry.created_at
	buyer_product["updated_at"] = buyer_product_entry.updated_at
	
	buyer_product["product"] = serialize_product(buyer_product_entry.product)

	return buyer_product