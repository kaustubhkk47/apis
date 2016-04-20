from ..models.seller import SellerAddress

def serialize_seller(seller_entry):

    seller_addresses_set = SellerAddress.objects.filter(seller_id = seller_entry.id)

    seller_addresses = serialize_seller_addresses(seller_addresses_set)


    seller = {
        "name" : seller_entry.name,
        "company_name" : seller_entry.company_name,
        "mobile_number" : seller_entry.mobile_number,
        "email" : seller_entry.email,
        "password" : seller_entry.password,
        "alternate_phone_number" : seller_entry.alternate_phone_number,
        "mobile_verification" : seller_entry.mobile_verification,
        "email_verification" : seller_entry.email_verification,
        "created_at" : seller_entry.created_at,
        "updated_at" : seller_entry.updated_at,
        "addresses" : seller_addresses
    }

    return seller


def serialize_seller_addresses(seller_addresses_set):

    seller_addresses =[]

    for seller_address in seller_addresses_set:

        seller_address_entry = {
            "address" : seller_address.address,
            "landmark" : seller_address.landmark,
            "city" : seller_address.city,
            "state" : seller_address.state,
            "country" : seller_address.country,
            "contact_number" : seller_address.contact_number
        }

        seller_addresses.append(seller_address_entry)

    return seller_addresses

def get_seller_details(seller_set):

    sellers = []

    for seller in seller_set:

        seller_entry = serialize_seller(seller)
        sellers.append(seller_entry)

    return sellers