from ..models.buyer import BuyerAddress

def serialize_buyer(buyer_entry):

    buyer_addresses_queryset = BuyerAddress.objects.filter(buyer__id = buyer_entry.id)

    buyer_addresses = serialize_buyer_addresses(buyer_addresses_queryset)

    buyer = {
        "name" : buyer_entry.name,
        "company_name" : buyer_entry.company_name,
        "mobile_number" : buyer_entry.mobile_number,
        "email" : buyer_entry.email,
        "password" : buyer_entry.password,
        "alternate_phone_number" : buyer_entry.alternate_phone_number,
        "mobile_verification" : buyer_entry.mobile_verification,
        "email_verification" : buyer_entry.email_verification,
        "gender" : buyer_entry.gender,
        "created_at" : buyer_entry.created_at,
        "updated_at" : buyer_entry.updated_at,
        "address" : buyer_addresses,

        "vat_number" : buyer_entry.buyerdetails.vat_number,
        "tin_number" : buyer_entry.buyerdetails.tin_number,
        "buyer_interest" : buyer_entry.buyerdetails.buyer_interest,
        "customer_type" : buyer_entry.buyerdetails.customer_type,
        "buying_capacity" : buyer_entry.buyerdetails.buying_capacity
    }

    return buyer


def serialize_buyer_addresses(buyer_addresses_queryset):

    buyer_addresses =[]

    for buyer_address in buyer_addresses_queryset:

        buyer_address_entry = {
            "address" : buyer_address.address,
            "landmark" : buyer_address.landmark,
            "city" : buyer_address.city,
            "state" : buyer_address.state,
            "country" : buyer_address.country,
            "contact_number" : buyer_address.contact_number
        }

        buyer_addresses.append(buyer_address_entry)

    return buyer_addresses

def parse_buyer(buyers_queryset):

    buyers = []

    for buyer in buyers_queryset:
        buyer_entry = serialize_buyer(buyer)
        buyers.append(buyer_entry)

    return buyers