from ..models.buyer import BuyerAddress

def serialize_buyer(buyer_entry):

    buyer_addresses_set = BuyerAddress.objects.filter(buyer_id = buyer_entry.id)

    buyer_addresses = serialize_buyer_addresses(buyer_addresses_set)


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
        "vat_number" : buyer_entry.vat_number,
        "tin_number" : buyer_entry.tin_number,
        "buyer_interest" : buyer_entry.buyer_interest,
        "customer_type" : buyer_entry.customer_type,
        "buying_capacity" : buyer_entry.buying_capacity,
        "created_at" : buyer_entry.created_at,
        "updated_at" : buyer_entry.updated_at,
        "addresses" : buyer_addresses
    }

    return buyer


def serialize_buyer_addresses(buyer_addresses_set):

    buyer_addresses =[]

    for buyer_address in buyer_addresses_set:

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

def get_buyer_details(buyers_set):

    buyers = []

    for buyer in buyers_set:

        buyer_entry = serialize_buyer(buyer)
        buyers.append(buyer_entry)

    return buyers