from django.db import models
from scripts.utils import validate_date_time

class Seller(models.Model):
    name = models.CharField(max_length=200, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    mobile_number = models.CharField(max_length=11, blank=False, db_index=True)
    email = models.EmailField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    alternate_phone_number = models.CharField(max_length=11, blank=True)
    mobile_verification = models.BooleanField(default=False)
    email_verification = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    delete_status = models.BooleanField(default=False)

    def __unicode__(self):
        return self.company_name

class SellerAddress(models.Model):
    seller = models.ForeignKey(Seller)

    address = models.CharField(max_length=255, blank=True, null=False)
    landmark = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True, default="India")
    contact_number = models.CharField(max_length=11, blank=True)
    pincode = models.CharField(max_length=6, blank=True)

    def __unicode__(self):
        return self.seller.name

class SellerDetails(models.Model):

    seller = models.OneToOneField(Seller)

    vat_tin = models.CharField(max_length=20, blank=True)
    cst = models.CharField(max_length=20, blank=True)

    pan = models.CharField(max_length=10, blank=True, null=False)
    name_on_pan = models.CharField(max_length=100, blank=True, null=False)
    dob_on_pan = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)

    pan_verification = models.BooleanField(default=0, blank=False, null=False)
    tin_verification = models.BooleanField(default=0, blank=False, null=False)

    def __unicode__(self):
        return self.seller.name

class SellerBankDetails(models.Model):

    seller = models.ForeignKey(Seller)

    account_holders_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=18, blank=True)
    ifsc = models.CharField(max_length=11, blank=True)
    bank_name = models.CharField(max_length=50, blank=True)

    branch  = models.CharField(max_length=200, blank=True)
    branch_city = models.CharField(max_length=50, blank=True)
    branch_pincode = models.CharField(max_length=6, blank=True)

    def __unicode__(self):
        return self.seller.name

def validateSellerData(seller, oldseller, isnew):

    flag = 0

    if not "name" in seller or not seller["name"]:
        flag = 1
        seller["name"] = oldseller.name
    if not "company_name" in seller or not seller["company_name"]:
        seller["company_name"] = oldseller.company_name
    if not "mobile_number" in seller or not seller["mobile_number"]:
        flag = 1
        seller["mobile_number"] = oldseller.mobile_number
    if not "email" in seller or not seller["email"]:
        seller["email"] = oldseller.email
    if not "password" in seller or not seller["password"]:
        seller["password"] = oldseller.password
    if not "alternate_phone_number" in seller or not seller["alternate_phone_number"]:
        seller["alternate_phone_number"] = oldseller.alternate_phone_number
    if not "mobile_verification" in seller or not seller["mobile_verification"]:
        seller["mobile_verification"] = oldseller.mobile_verification
    if not "email_verification" in seller or not seller["email_verification"]:
        seller["email_verification"] = oldseller.email_verification

    if isnew == 1 and flag == 1:
        return False

    return True

def validateSellerAddressData(selleraddress, oldselleraddress):

    if not "address" in selleraddress or not selleraddress["address"]:
        selleraddress["address"] = oldselleraddress.address
    if not "landmark" in selleraddress or not selleraddress["landmark"]:
        selleraddress["landmark"] = oldselleraddress.landmark
    if not "city" in selleraddress or not selleraddress["city"]:
        selleraddress["city"] = oldselleraddress.city
    if not "state" in selleraddress or not selleraddress["state"]:
        selleraddress["state"] = oldselleraddress.state
    if not "country" in selleraddress or not selleraddress["country"]:
        selleraddress["country"] = oldselleraddress.country
    if not "contact_number" in selleraddress or not selleraddress["contact_number"]:
        selleraddress["contact_number"] = oldselleraddress.contact_number
    if not "pincode" in selleraddress or not selleraddress["pincode"]:
        selleraddress["pincode"] = oldselleraddress.pincode

def validateSellerDetailsData(sellerdetails, oldsellerdetails):
    if not "vat_tin" in sellerdetails or not sellerdetails["vat_tin"]:
        sellerdetails["vat_tin"] = oldsellerdetails.vat_tin
    if not "cst" in sellerdetails or not sellerdetails["cst"]:
        sellerdetails["cst"] = oldsellerdetails.cst
    if not "pan" in sellerdetails or not sellerdetails["pan"]:
        sellerdetails["pan"] = oldsellerdetails.pan
    if not "name_on_pan" in sellerdetails or not sellerdetails["name_on_pan"]:
        sellerdetails["name_on_pan"] = oldsellerdetails.name_on_pan
    if not "dob_on_pan" in sellerdetails or not sellerdetails["dob_on_pan"] or not validate_date_time(sellerdetails["dob_on_pan"]):
        sellerdetails["dob_on_pan"] = oldsellerdetails.dob_on_pan
    if not "pan_verification" in sellerdetails or not sellerdetails["pan_verification"]:
        sellerdetails["pan_verification"] = oldsellerdetails.pan_verification
    if not "tin_verification" in sellerdetails or not sellerdetails["tin_verification"]:
        sellerdetails["tin_verification"] = oldsellerdetails.tin_verification

def validateSellerBankdetailsData(sellerbankdetails, oldsellerbankdetails):

    if not "account_holders_name" in sellerbankdetails or not sellerbankdetails["account_holders_name"]:
        sellerbankdetails["account_holders_name"] = oldsellerbankdetails.account_holders_name
    if not "account_number" in sellerbankdetails or not sellerbankdetails["account_number"]:
        sellerbankdetails["account_number"] = oldsellerbankdetails.account_number
    if not "ifsc" in sellerbankdetails or not sellerbankdetails["ifsc"]:
        sellerbankdetails["ifsc"] = oldsellerbankdetails.ifsc
    if not "bank_name" in sellerbankdetails or not sellerbankdetails["bank_name"]:
        sellerbankdetails["bank_name"] = oldsellerbankdetails.bank_name
    if not "branch" in sellerbankdetails or not sellerbankdetails["branch"]:
        sellerbankdetails["branch"] = oldsellerbankdetails.branch
    if not "branch_city" in sellerbankdetails or not sellerbankdetails["branch_city"]:
        sellerbankdetails["branch_city"] = oldsellerbankdetails.branch_city
    if not "branch_pincode" in sellerbankdetails or not sellerbankdetails["branch_pincode"]:
        sellerbankdetails["branch_pincode"] = oldsellerbankdetails.branch_pincode 

def populateSellerData(sellerPtr, seller):
    sellerPtr.name = seller["name"]
    sellerPtr.company_name = seller["company_name"]
    sellerPtr.mobile_number = seller["mobile_number"]
    sellerPtr.email = seller["email"]
    sellerPtr.password = seller["password"]
    sellerPtr.alternate_phone_number = seller["alternate_phone_number"]
    sellerPtr.mobile_verification = bool(seller["mobile_verification"])
    sellerPtr.email_verification = bool(seller["email_verification"])

def populateSellerDetailsData(sellerDetailsPtr,sellerdetails):
    sellerDetailsPtr.cst = sellerdetails["cst"]
    sellerDetailsPtr.pan = sellerdetails["pan"]
    sellerDetailsPtr.name_on_pan = sellerdetails["name_on_pan"]
    sellerDetailsPtr.dob_on_pan = sellerdetails["dob_on_pan"]
    sellerDetailsPtr.pan_verification = bool(sellerdetails["pan_verification"])
    sellerDetailsPtr.tin_verification = bool(sellerdetails["tin_verification"])
    sellerDetailsPtr.vat_tin = sellerdetails["vat_tin"]

def populateSellerAddressData(sellerAddressPtr, selleraddress):
    sellerAddressPtr.address = selleraddress["address"]
    sellerAddressPtr.landmark = selleraddress["landmark"]
    sellerAddressPtr.city = selleraddress["city"]
    sellerAddressPtr.state = selleraddress["state"]
    sellerAddressPtr.country = selleraddress["country"]
    sellerAddressPtr.contact_number = selleraddress["contact_number"]
    sellerAddressPtr.pincode = selleraddress["pincode"]

def populateSellerBankDetailsData(sellerBankDetailsPtr,sellerbankdetails):
    sellerBankDetailsPtr.account_holders_name = sellerbankdetails["account_holders_name"]
    sellerBankDetailsPtr.account_number = sellerbankdetails["account_number"]
    sellerBankDetailsPtr.ifsc = sellerbankdetails["ifsc"]
    sellerBankDetailsPtr.bank_name = sellerbankdetails["bank_name"]
    sellerBankDetailsPtr.branch = sellerbankdetails["branch"]
    sellerBankDetailsPtr.branch_city = sellerbankdetails["branch_city"]
    sellerBankDetailsPtr.branch_pincode = sellerbankdetails["branch_pincode"]