from ..models.seller import Seller, SellerAddress, SellerBankDetails, filterSeller
from .businesstype import serialize_business_type

def serialize_seller(seller_entry, parameters = {}):

	seller = {}

	seller["sellerID"] = seller_entry.id
	seller["name"] = seller_entry.name
	seller["company_name"] = seller_entry.company_name
	seller["mobile_number"] = seller_entry.mobile_number
	seller["email"] = seller_entry.email
	seller["alternate_phone_number"] = seller_entry.alternate_phone_number
	seller["mobile_verification"] = seller_entry.mobile_verification
	seller["email_verification"] = seller_entry.email_verification
	seller["created_at"] = seller_entry.created_at
	seller["updated_at"] = seller_entry.updated_at
	seller["company_profile"] = seller_entry.company_profile
	seller["seller_conditions"] = seller_entry.seller_conditions
	seller["concerned_person"] = seller_entry.concerned_person
	seller["concerned_person_number"] = seller_entry.concerned_person_number
	seller["show_online"] = seller_entry.show_online
	
	if "seller_details_details" in parameters and parameters["seller_details_details"] == 1 and hasattr(seller_entry,'sellerdetails'):
		seller_details = {}
		seller_details["detailsID"] = seller_entry.sellerdetails.id
		seller_details["vat_tin"] = seller_entry.sellerdetails.vat_tin
		seller_details["cst"] = seller_entry.sellerdetails.cst
		seller_details["pan"] = seller_entry.sellerdetails.pan
		seller_details["name_on_pan"] = seller_entry.sellerdetails.name_on_pan
		seller_details["dob_on_pan"] = seller_entry.sellerdetails.dob_on_pan
		seller_details["pan_verification"] = seller_entry.sellerdetails.pan_verification
		seller_details["tin_verification"] = seller_entry.sellerdetails.tin_verification
		if hasattr(seller_entry.sellerdetails, "seller_type") and seller_entry.sellerdetails.seller_type != None:
			seller_details["seller_type"] = serialize_business_type(seller_entry.sellerdetails.seller_type)

		seller["details"] = seller_details

	if "seller_address_details" in parameters and parameters["seller_address_details"] == 1:
		seller_addresses_queryset = SellerAddress.objects.filter(seller_id = seller_entry.id)
		seller_addresses = serialize_seller_addresses(seller_addresses_queryset)
		seller["address"] = seller_addresses
	
	if "seller_bank_details" in parameters and parameters["seller_bank_details"] == 1:
	   seller_bankdetails_queryset = SellerBankDetails.objects.filter(seller_id = seller_entry.id)
	   seller_bankdetails = serialize_seller_bankdetails(seller_bankdetails_queryset)
	   seller["bank_details"] = seller_bankdetails

	return seller


def serialize_seller_addresses(seller_addresses_queryset, parameters = {}):

	seller_addresses =[]

	for seller_address in seller_addresses_queryset:
		seller_address_entry = serialize_seller_address(seller_address,parameters)
		seller_addresses.append(seller_address_entry)

	return seller_addresses

def serialize_seller_address(seller_address, parameters = {}):
	seller_address_entry = {
		"addressID" : seller_address.id,
		"address" : seller_address.address_line,
		"landmark" : seller_address.landmark,
		"city" : seller_address.city_name,
		"state" : seller_address.state_name,
		"country" : seller_address.country_name,
		"contact_number" : seller_address.contact_number,
		"pincode" : seller_address.pincode_number,
		"created_at":seller_address.created_at,
		"updated_at":seller_address.updated_at
	}
	return seller_address_entry

def serialize_seller_bankdetails(seller_bankdetails_queryset, parameters = {}):
	
	seller_bankdetails =[]
	
	for seller_bankdetail in seller_bankdetails_queryset:
		
		seller_bankdetails_entry = {
			"bank_detailsID" : seller_bankdetail.id,
			"account_holders_name" : seller_bankdetail.account_holders_name,
			"account_number" : seller_bankdetail.account_number,
			"ifsc" : seller_bankdetail.ifsc,
			"bank_name" : seller_bankdetail.bank_name,
			"branch" : seller_bankdetail.branch,
			"branch_city" : seller_bankdetail.branch_city,
			"branch_pincode" : seller_bankdetail.branch_pincode
		}

		seller_bankdetails.append(seller_bankdetails_entry)

	return seller_bankdetails

def parse_seller(seller_queryset, parameters = {}):

	sellers = []

	for seller in seller_queryset:
		seller_entry = serialize_seller(seller, parameters)
		sellers.append(seller_entry)

	return sellers

def parse_seller_category(seller_category_queryset, parameters = {}):

	seller_categories = []

	for seller_category in seller_category_queryset:
		seller_category_entry = serialize_seller_category(seller_category, parameters)
		seller_categories.append(seller_category_entry)

	return seller_categories

def serialize_seller_category(seller_category_entry, parameters):

	seller_category = {}

	seller_category["sellercategoryID"] = seller_category_entry.id

	seller = {}
	seller["sellerID"] = seller_category_entry.seller.id
	seller["company_name"] = seller_category_entry.seller.company_name
	seller_category["seller"] = seller

	#category = {}
	#category["categoryID"] = seller_category_entry.category_id
	#seller_category["category"] = category

	return seller_category