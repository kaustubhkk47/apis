from ..models.seller import SellerAddress, SellerBankDetails

def serialize_seller(seller_entry):
    
    seller_addresses_queryset = SellerAddress.objects.filter(seller__id = seller_entry.id)
    seller_addresses = serialize_seller_addresses(seller_addresses_queryset)
    
    seller_bankdetails_queryset = SellerBankDetails.objects.filter(seller__id = seller_entry.id)
    seller_bankdetails = serialize_seller_bankdetails(seller_bankdetails_queryset)
    
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
        "address" : seller_addresses,
        "bankdetails" : seller_bankdetails
    }
    
    if hasattr(seller_entry,'sellerdetails'):
        seller_details = {}
        seller_details["detailsID"] = seller_entry.sellerdetails.id
        seller_details["vat_tin"] = seller_entry.sellerdetails.vat_tin
        seller_details["cst"] = seller_entry.sellerdetails.cst
        seller_details["pan"] = seller_entry.sellerdetails.pan
        seller_details["name_on_pan"] = seller_entry.sellerdetails.name_on_pan
        seller_details["dob_on_pan"] = seller_entry.sellerdetails.dob_on_pan
        seller_details["pan_verification"] = seller_entry.sellerdetails.pan_verification
        seller_details["tin_verification"] = seller_entry.sellerdetails.tin_verification

        seller["details"] = seller_details

    return seller


def serialize_seller_addresses(seller_addresses_queryset):

    seller_addresses =[]

    for seller_address in seller_addresses_queryset:
        seller_address_entry = serialize_seller_address(seller_address)
        seller_addresses.append(seller_address_entry)

    return seller_addresses

def serialize_seller_address(seller_address):
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
    return seller_address_entry

def serialize_seller_bankdetails(seller_bankdetails_queryset):
    
    seller_bankdetails =[]
    
    for seller_bankdetail in seller_bankdetails_queryset:
        
        seller_bankdetails_entry = {
            "bankdetailsID" : seller_bankdetail.id,
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

def parse_seller(seller_queryset):

    sellers = []

    for seller in seller_queryset:
        seller_entry = serialize_seller(seller)
        sellers.append(seller_entry)

    return sellers