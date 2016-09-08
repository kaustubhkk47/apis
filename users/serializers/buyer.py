from ..models.buyer import *
from catalog.serializers.category import serialize_categories
from catalog.serializers.product import serialize_product
from address.serializers.state import serialize_state
from .businesstype import serialize_business_type
import time
def serialize_buyer(buyer_entry, parameters = {}):

	buyer = {}

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
	buyer["buyer_panel_url"] = str(buyer_entry.id) + "-" + str(int(time.mktime(buyer_entry.created_at.timetuple())))
	buyer["store_url"] = buyer_entry.store_url
	buyer["store_global_discount"] = buyer_entry.store_global_discount
	
	if "buyer_details_details" in parameters and parameters["buyer_details_details"] == 1 and hasattr(buyer_entry,'buyerdetails'):
		buyer_details = {}
		buyer_details["detailsID"] = buyer_entry.buyerdetails.id
		buyer_details["vat_tin"] = buyer_entry.buyerdetails.vat_tin
		buyer_details["cst"] = buyer_entry.buyerdetails.cst
		buyer_details["customer_type"] = buyer_entry.buyerdetails.customer_type
		buyer_details["buying_capacity"] = buyer_entry.buyerdetails.buying_capacity
		buyer_details["purchase_duration"] = buyer_entry.buyerdetails.purchase_duration
		if hasattr(buyer_entry.buyerdetails, "buyer_type") and buyer_entry.buyerdetails.buyer_type != None:
			buyer_details["buyer_type"] = serialize_business_type(buyer_entry.buyerdetails.buyer_type)

		buyer["details"] = buyer_details

	if "buyer_interest_details" in parameters and parameters["buyer_interest_details"] == 1:
	   buyerInterestQuerySet = filterBuyerInterest(parameters)
	   buyerInterestQuerySet = buyerInterestQuerySet.filter(buyer_id = buyer_entry.id)
	   buyer["buyer_interests"] = parse_buyer_interest(buyerInterestQuerySet,parameters)

	if "buyer_product_details" in parameters and parameters["buyer_product_details"] == 1:
		tempParameters = parameters.copy()
		tempParameters["buyer_interest_active"] = True
		tempParameters["buyer_product_delete_status"] = False
		tempParameters["buyer_product_is_active"] = True
		tempParameters["responded"] = 0
		tempParameters["buyer_product_shared_on_whatsapp"] = False
		print tempParameters
		buyerProductQuerySet = filterBuyerProducts(tempParameters)
		buyerProductQuerySet = buyerProductQuerySet.filter(buyer_id = buyer_entry.id)
		buyerProductQuerySet = buyerProductQuerySet[:parameters["buyer_product_count"]]
		buyer["buyer_products"] = parse_buyer_product(buyerProductQuerySet,parameters)

	if "buyer_address_details" in parameters and parameters["buyer_address_details"] == 1:
		buyer_addresses_queryset = BuyerAddress.objects.filter(buyer_id = buyer_entry.id)
		buyer_addresses = parse_buyer_address(buyer_addresses_queryset, parameters)
		buyer["address"] = buyer_addresses

	if "buyer_purchasing_state_details" in parameters and parameters["buyer_purchasing_state_details"] == 1:
		buyer_purchasing_state_queryset = filterBuyerPurchasingState(parameters)
		buyer_purchasing_state_queryset = buyer_purchasing_state_queryset.filter(buyer_id=buyer_entry.id)
		buyer_purchasing_state = parse_buyer_purchasing_state(buyer_purchasing_state_queryset, parameters)
		buyer["purchasing_states"] = buyer_purchasing_state

	if "buyer_buys_from_details" in parameters and parameters["buyer_buys_from_details"] == 1:
		buyer_buys_from_queryset = filterBuyerBuysFrom(parameters)
		buyer_buys_from_queryset = buyer_buys_from_queryset.filter(buyer_id=buyer_entry.id)
		buyer_buys_from = parse_buyer_buys_from(buyer_buys_from_queryset, parameters)
		buyer["buys_from"] = buyer_buys_from

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

def parse_buyer_product_response(buyer_products_queryset, parameters = {}):

	buyer_products = []

	for buyer_product in buyer_products_queryset:
		buyer_product_entry = serialize_buyer_product_response(buyer_product, parameters)
		buyer_products.append(buyer_product_entry)

	return buyer_products

def serialize_buyer_product(buyer_product_entry, parameters = {}):

	buyer_product = {}

	buyer_product["buyerproductID"] = buyer_product_entry.id
	buyer_product["buyerID"] = buyer_product_entry.buyer_id
	if hasattr(buyer_product_entry,"buyer_interest"):
		buyer_product["buyerinterestID"] = buyer_product_entry.buyer_interest_id
	buyer_product["is_active"] = buyer_product_entry.is_active
	buyer_product["responded"] = buyer_product_entry.responded
	buyer_product["created_at"] = buyer_product_entry.created_at
	buyer_product["updated_at"] = buyer_product_entry.updated_at
	
	buyer_product["product"] = serialize_product(buyer_product_entry.product, parameters)

	return buyer_product

def serialize_buyer_product_response(buyer_product_entry, parameters = {}):

	buyer_product = {}

	buyer_product["buyerproductresponseID"] = buyer_product_entry.id
	buyer_product["buyerID"] = buyer_product_entry.buyer_id
	buyer_product["buyerproductID"] = buyer_product_entry.buyer_product_id
	buyer_product["response_code"] = buyer_product_entry.response_code
	buyer_product["has_swiped"] = buyer_product_entry.has_swiped
	buyer_product["created_at"] = buyer_product_entry.created_at
	buyer_product["updated_at"] = buyer_product_entry.updated_at
	buyer_product["store_discount"] = buyer_product_entry.store_discount
	
	buyer_product["product"] = serialize_product(buyer_product_entry.product, parameters)

	return buyer_product

def parse_buyer_purchasing_state(buyer_purchasing_states_queryset, parameters = {}):

	buyer_purchasing_states =[]

	for buyer_purchasing_state in buyer_purchasing_states_queryset:

		buyer_purchasing_state_entry = serialize_buyer_purchasing_state(buyer_purchasing_state, parameters)
		buyer_purchasing_states.append(buyer_purchasing_state_entry)

	return buyer_purchasing_states

def serialize_buyer_purchasing_state(buyer_purchasing_state_entry, parameters = {}):

	buyer_purchasing_state = {}
	buyer_purchasing_state["buyerpurchasingstateID"] = buyer_purchasing_state_entry.id
	buyer_purchasing_state["buyerID"] = buyer_purchasing_state_entry.buyer_id
	buyer_purchasing_state["created_at"] = buyer_purchasing_state_entry.created_at
	buyer_purchasing_state["updated_at"] = buyer_purchasing_state_entry.updated_at
	buyer_purchasing_state["delete_status"] = buyer_purchasing_state_entry.delete_status

	buyer_purchasing_state["state"] = serialize_state(buyer_purchasing_state_entry.state)

	return buyer_purchasing_state

def parse_buyer_buys_from(buyer_buys_from_entry, parameters = {}):

	buyer_buys_froms =[]

	for buyer_buys_from in buyer_buys_from_entry:

		buyer_buys_from_entry = serialize_buyer_buys_from(buyer_buys_from, parameters)
		buyer_buys_froms.append(buyer_buys_from_entry)

	return buyer_buys_froms

def serialize_buyer_buys_from(buyer_buys_from_entry, parameters = {}):

	buyer_buys_from = {}
	buyer_buys_from["buyerbuysfromID"] = buyer_buys_from_entry.id
	buyer_buys_from["buyerID"] = buyer_buys_from_entry.buyer_id
	buyer_buys_from["created_at"] = buyer_buys_from_entry.created_at
	buyer_buys_from["updated_at"] = buyer_buys_from_entry.updated_at

	buyer_buys_from["business_type"] = serialize_business_type(buyer_buys_from_entry.business_type)

	return buyer_buys_from

def parse_buyer_store_lead(buyer_store_leads_queryset, parameters = {}):

	buyer_store_leads = []

	for buyer_store_lead in buyer_store_leads_queryset:
		buyer_store_lead_entry = serialize_buyer_store_lead(buyer_store_lead, parameters)
		buyer_store_leads.append(buyer_store_lead_entry)

	return buyer_store_leads

def serialize_buyer_store_lead(buyer_store_lead_entry, parameters = {}):

	buyer_store_lead = {}
	buyer_store_lead["buyerstoreleadID"] = buyer_store_lead_entry.id
	buyer_store_lead["buyerID"] = buyer_store_lead_entry.buyer_id
	buyer_store_lead["name"] = buyer_store_lead_entry.name
	buyer_store_lead["mobile_number"] = buyer_store_lead_entry.mobile_number
	buyer_store_lead["email"] = buyer_store_lead_entry.email
	buyer_store_lead["status"] = buyer_store_lead_entry.status
	buyer_store_lead["sizes"] = buyer_store_lead_entry.sizes
	buyer_store_lead["quantity"] = buyer_store_lead_entry.quantity
	
	buyer_store_lead["product"] = serialize_product(buyer_store_lead_entry.product, parameters)

	return buyer_store_lead