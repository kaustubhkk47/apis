from django.db import models
from django.contrib import admin
from scripts.utils import validate_date

#Make changes in model, validate, populate and serializer 

class Seller(models.Model):
    name = models.CharField(max_length=200, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    mobile_number = models.CharField(max_length=11, blank=False, db_index=True)
    email = models.EmailField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    alternate_phone_number = models.CharField(max_length=11, blank=True)
    mobile_verification = models.BooleanField(default=False)
    email_verification = models.BooleanField(default=False)
    company_profile = models.TextField(blank=True)
    seller_conditions = models.TextField(blank=True)
    concerned_person = models.TextField(blank=True,default="")
    concerned_person_number = models.TextField(blank=True,default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    delete_status = models.BooleanField(default=False)
    show_online = models.BooleanField(default=True)

    def __unicode__(self):
        return str(self.id) + " - " +self.name + " - " + self.company_name + " - " + self.mobile_number

class SellerAdmin(admin.ModelAdmin):
    exclude = ('password',)

class SellerAddress(models.Model):
    seller = models.ForeignKey(Seller)

    address_line = models.CharField(max_length=255, blank=True, null=False)
    landmark = models.CharField(max_length=50, blank=True)
    city_name = models.CharField(max_length=50, blank=True)
    state_name = models.CharField(max_length=50, blank=True)
    country_name = models.CharField(max_length=50, blank=True, default="India")
    contact_number = models.CharField(max_length=11, blank=True)
    pincode_number = models.CharField(max_length=6, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.seller.id) + " - " +self.seller.name + " - " + self.seller.company_name + " - " + self.seller.mobile_number

class SellerDetails(models.Model):

    seller = models.OneToOneField(Seller)

    vat_tin = models.CharField(max_length=20, blank=True)
    cst = models.CharField(max_length=20, blank=True)

    pan = models.CharField(max_length=10, blank=True, null=False)
    name_on_pan = models.CharField(max_length=100, blank=True, null=False)
    dob_on_pan = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)

    pan_verification = models.BooleanField(default=0, blank=False, null=False)
    tin_verification = models.BooleanField(default=0, blank=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.seller.id) + " - " +self.seller.name + " - " + self.seller.company_name + " - " + self.seller.mobile_number

class SellerBankDetails(models.Model):

    seller = models.ForeignKey(Seller)

    account_holders_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=18, blank=True)
    ifsc = models.CharField(max_length=11, blank=True)
    bank_name = models.CharField(max_length=50, blank=True)

    branch  = models.CharField(max_length=200, blank=True)
    branch_city = models.CharField(max_length=50, blank=True)
    branch_pincode = models.CharField(max_length=6, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.seller.id) + " - " +self.seller.name + " - " + self.seller.company_name + " - " + self.seller.mobile_number

def validateSellerData(seller, oldseller, isnew):

    flag = 0

    if not "name" in seller or seller["name"]==None:
        flag = 1
        seller["name"] = oldseller.name
    if not "company_name" in seller or seller["company_name"]==None:
        seller["company_name"] = oldseller.company_name
    if not "mobile_number" in seller or seller["mobile_number"]==None:
        flag = 1
        seller["mobile_number"] = oldseller.mobile_number
    if not "email" in seller or seller["email"]==None:
        seller["email"] = oldseller.email
    if not "password" in seller or seller["password"]==None:
        seller["password"] = oldseller.password
    if not "alternate_phone_number" in seller or seller["alternate_phone_number"]==None:
        seller["alternate_phone_number"] = oldseller.alternate_phone_number
    if not "mobile_verification" in seller or seller["mobile_verification"]==None:
        seller["mobile_verification"] = oldseller.mobile_verification
    if not "email_verification" in seller or seller["email_verification"]==None:
        seller["email_verification"] = oldseller.email_verification
    if not "company_profile" in seller or seller["company_profile"]==None:
        seller["company_profile"] = oldseller.company_profile
    if not "seller_conditions" in seller or seller["seller_conditions"]==None:
        seller["seller_conditions"] = oldseller.seller_conditions
    if not "show_online" in seller or seller["show_online"]==None:
        seller["show_online"] = oldseller.show_online
    if not "concerned_person" in seller or seller["concerned_person"]==None:
        seller["concerned_person"] = oldseller.concerned_person
    if not "concerned_person_number" in seller or seller["concerned_person_number"]==None:
        seller["concerned_person_number"] = oldseller.concerned_person_number

    if isnew == 1 and flag == 1:
        return False

    return True

def validateSellerAddressData(selleraddress, oldselleraddress):

    if not "address" in selleraddress or selleraddress["address"]==None:
        selleraddress["address"] = oldselleraddress.address_line
    if not "landmark" in selleraddress or selleraddress["landmark"]==None:
        selleraddress["landmark"] = oldselleraddress.landmark
    if not "city" in selleraddress or selleraddress["city"]==None:
        selleraddress["city"] = oldselleraddress.city_name
    if not "state" in selleraddress or selleraddress["state"]==None:
        selleraddress["state"] = oldselleraddress.state_name
    if not "country" in selleraddress or selleraddress["country"]==None:
        selleraddress["country"] = oldselleraddress.country_name
    if not "contact_number" in selleraddress or selleraddress["contact_number"]==None:
        selleraddress["contact_number"] = oldselleraddress.contact_number
    if not "pincode" in selleraddress or selleraddress["pincode"]==None:
        selleraddress["pincode"] = oldselleraddress.pincode_number

def validateSellerDetailsData(sellerdetails, oldsellerdetails):
    if not "vat_tin" in sellerdetails or sellerdetails["vat_tin"]==None:
        sellerdetails["vat_tin"] = oldsellerdetails.vat_tin
    if not "cst" in sellerdetails or sellerdetails["cst"]==None:
        sellerdetails["cst"] = oldsellerdetails.cst
    if not "pan" in sellerdetails or sellerdetails["pan"]==None:
        sellerdetails["pan"] = oldsellerdetails.pan
    if not "name_on_pan" in sellerdetails or sellerdetails["name_on_pan"]==None:
        sellerdetails["name_on_pan"] = oldsellerdetails.name_on_pan
    if not "dob_on_pan" in sellerdetails or sellerdetails["dob_on_pan"]==None or not validate_date(sellerdetails["dob_on_pan"]):
        sellerdetails["dob_on_pan"] = oldsellerdetails.dob_on_pan
    if not "pan_verification" in sellerdetails or sellerdetails["pan_verification"]==None:
        sellerdetails["pan_verification"] = oldsellerdetails.pan_verification
    if not "tin_verification" in sellerdetails or sellerdetails["tin_verification"]==None:
        sellerdetails["tin_verification"] = oldsellerdetails.tin_verification

def validateSellerBankdetailsData(sellerbankdetails, oldsellerbankdetails):

    if not "account_holders_name" in sellerbankdetails or sellerbankdetails["account_holders_name"]==None:
        sellerbankdetails["account_holders_name"] = oldsellerbankdetails.account_holders_name
    if not "account_number" in sellerbankdetails or sellerbankdetails["account_number"]==None:
        sellerbankdetails["account_number"] = oldsellerbankdetails.account_number
    if not "ifsc" in sellerbankdetails or sellerbankdetails["ifsc"]==None:
        sellerbankdetails["ifsc"] = oldsellerbankdetails.ifsc
    if not "bank_name" in sellerbankdetails or sellerbankdetails["bank_name"]==None:
        sellerbankdetails["bank_name"] = oldsellerbankdetails.bank_name
    if not "branch" in sellerbankdetails or sellerbankdetails["branch"]==None:
        sellerbankdetails["branch"] = oldsellerbankdetails.branch
    if not "branch_city" in sellerbankdetails or sellerbankdetails["branch_city"]==None:
        sellerbankdetails["branch_city"] = oldsellerbankdetails.branch_city
    if not "branch_pincode" in sellerbankdetails or sellerbankdetails["branch_pincode"]==None:
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
    sellerPtr.company_profile = seller["company_profile"]
    sellerPtr.seller_conditions = seller["seller_conditions"]
    sellerPtr.show_online = seller["show_online"]
    sellerPtr.concerned_person = seller["concerned_person"]
    sellerPtr.concerned_person_number = seller["concerned_person_number"]

def populateSellerDetailsData(sellerDetailsPtr,sellerdetails):
    sellerDetailsPtr.cst = sellerdetails["cst"]
    sellerDetailsPtr.pan = sellerdetails["pan"]
    sellerDetailsPtr.name_on_pan = sellerdetails["name_on_pan"]
    sellerDetailsPtr.dob_on_pan = sellerdetails["dob_on_pan"]
    sellerDetailsPtr.pan_verification = bool(sellerdetails["pan_verification"])
    sellerDetailsPtr.tin_verification = bool(sellerdetails["tin_verification"])
    sellerDetailsPtr.vat_tin = sellerdetails["vat_tin"]

def populateSellerAddressData(sellerAddressPtr, selleraddress):
    sellerAddressPtr.address_line = selleraddress["address"]
    sellerAddressPtr.landmark = selleraddress["landmark"]
    sellerAddressPtr.city_name = selleraddress["city"]
    sellerAddressPtr.state_name = selleraddress["state"]
    sellerAddressPtr.country_name = selleraddress["country"]
    sellerAddressPtr.contact_number = selleraddress["contact_number"]
    sellerAddressPtr.pincode_number = selleraddress["pincode"]

def populateSellerBankDetailsData(sellerBankDetailsPtr,sellerbankdetails):
    sellerBankDetailsPtr.account_holders_name = sellerbankdetails["account_holders_name"]
    sellerBankDetailsPtr.account_number = sellerbankdetails["account_number"]
    sellerBankDetailsPtr.ifsc = sellerbankdetails["ifsc"]
    sellerBankDetailsPtr.bank_name = sellerbankdetails["bank_name"]
    sellerBankDetailsPtr.branch = sellerbankdetails["branch"]
    sellerBankDetailsPtr.branch_city = sellerbankdetails["branch_city"]
    sellerBankDetailsPtr.branch_pincode = sellerbankdetails["branch_pincode"]

def sellerEmailExists(email):
    sellerPtr = Seller.objects.filter(email=email)

    if len(sellerPtr) > 0:
        return True

    return False

def sellerMobileNumberExists(mobileNumber):
    sellerPtr = Seller.objects.filter(mobile_number=mobileNumber)

    if len(sellerPtr) > 0:
        return True

    return False