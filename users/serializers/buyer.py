from ..models.buyer import BuyerAddress, BuyerDetails

def serialize_buyer(buyer_entry):

    buyer_addresses_queryset = BuyerAddress.objects.filter(buyer_id = buyer_entry.id)

    buyer_addresses = serialize_buyer_addresses(buyer_addresses_queryset)

    buyer = {
        "buyerID" : buyer_entry.id,
        "name" : buyer_entry.name,
        "company_name" : buyer_entry.company_name,
        "mobile_number" : buyer_entry.mobile_number,
        "email" : buyer_entry.email,
        "alternate_phone_number" : buyer_entry.alternate_phone_number,
        "mobile_verification" : buyer_entry.mobile_verification,
        "email_verification" : buyer_entry.email_verification,
        "gender" : buyer_entry.gender,
        "created_at" : buyer_entry.created_at,
        "updated_at" : buyer_entry.updated_at,
        "address" : buyer_addresses
    }    
    
    if hasattr(buyer_entry,'buyerdetails'):
        buyer_details = {}
        buyer_details["detailsID"] = buyer_entry.buyerdetails.id
        buyer_details["vat_tin"] = buyer_entry.buyerdetails.vat_tin
        buyer_details["cst"] = buyer_entry.buyerdetails.cst
        buyer_details["customer_type"] = buyer_entry.buyerdetails.customer_type
        buyer_details["buying_capacity"] = buyer_entry.buyerdetails.buying_capacity
        buyer_details["buys_from"] = buyer_entry.buyerdetails.buys_from
        buyer_details["purchasing_states"] = buyer_entry.buyerdetails.purchasing_states

        buyer["details"] = buyer_details

    return buyer


def serialize_buyer_addresses(buyer_addresses_queryset):

    buyer_addresses =[]

    for buyer_address in buyer_addresses_queryset:

        buyer_address_entry = serialize_buyer_address(buyer_address)
        buyer_addresses.append(buyer_address_entry)

    return buyer_addresses

def serialize_buyer_address(buyer_address):
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

def parse_buyer(buyers_queryset):

    buyers = []

    for buyer in buyers_queryset:
        buyer_entry = serialize_buyer(buyer)
        buyers.append(buyer_entry)

    return buyers