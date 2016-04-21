from ..models.seller import SellerAddress

def serialize_seller(seller_entry):

    seller_addresses_queryset = SellerAddress.objects.filter(seller__id = seller_entry.id)

    seller_addresses = serialize_seller_addresses(seller_addresses_queryset)

    seller = {
        "sellerID" : seller_entry.id,
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
        "address" : seller_addresses
    }


    if hasattr(seller_entry,'sellerdetails'):
        seller_details = {}
        seller_details["detailsID"] = seller_entry.sellerdetails.id
        seller_details["vat_tin"] = seller_entry.sellerdetails.vat_tin
        seller_details["cst"] = seller_entry.sellerdetails.cst
        seller_details["account_holders_name"] = seller_entry.sellerdetails.account_holders_name
        seller_details["account_number"] = seller_entry.sellerdetails.account_number
        seller_details["ifsc"] = seller_entry.sellerdetails.ifsc
        seller_details["pan"] = seller_entry.sellerdetails.pan
        seller_details["name_on_pan"] = seller_entry.sellerdetails.name_on_pan
        seller_details["dob_on_pan"] = seller_entry.sellerdetails.dob_on_pan
        seller_details["pan_verification"] = seller_entry.sellerdetails.pan_verification
        seller_details["tin_verification"] = seller_entry.sellerdetails.tin_verification

        seller["details"] = seller_details


    return seller


def serialize_seller_addresses(seller_addresses_queryset):

    seller_addresses =[]

    if len(seller_addresses_queryset) == 0:
        seller_address_entry = {
            "address" : None,
            "landmark" : None,
            "city" : None,
            "state" : None,
            "country" : None,
            "contact_number" : None,
            "pincode" : None
        }
        seller_addresses.append(seller_address_entry)

    for seller_address in seller_addresses_queryset:

        seller_address_entry = {
            "addressID" : seller_address.id,
            "address" : seller_address.address,
            "landmark" : seller_address.landmark,
            "city" : seller_address.city,
            "state" : seller_address.state,
            "country" : seller_address.country,
            "contact_number" : seller_address.contact_number,
            "pincode" : seller_address.pincode
        }

        seller_addresses.append(seller_address_entry)

    return seller_addresses

def parse_seller(seller_queryset):

    sellers = []

    for seller in seller_queryset:
        seller_entry = serialize_seller(seller)
        sellers.append(seller_entry)

    return sellers