from django.db import models

from scripts.utils import validate_mobile_number, validate_email, validate_bool, validate_pincode, validate_integer

from catalog.models.category import Category
from address.models.state import State
from address.models.pincode import Pincode

from .businessType import BusinessType

#Make changes in model, validate, populate and serializer 

class Buyer(models.Model):
    name = models.CharField(max_length=200, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    mobile_number = models.CharField(max_length=11, blank=False, db_index=True)
    email = models.EmailField(max_length=255, blank=True, null = True)
    password = models.CharField(max_length=255, blank=True)
    alternate_phone_number = models.CharField(max_length=11, blank=True)
    mobile_verification = models.BooleanField(default=False)
    email_verification = models.BooleanField(default=False)
    gender = models.CharField(max_length=10, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    blocked = models.BooleanField(default=False)
    delete_status = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.id) + " - " + self.name + " - " + self.company_name + " - " + self.mobile_number

class BuyerAddress(models.Model):
    buyer = models.ForeignKey(Buyer)
    pincode = models.ForeignKey(Pincode, blank=True,null=True)

    address_line = models.CharField(max_length=255, blank=True, null=False)
    landmark = models.CharField(max_length=50, blank=True)
    city_name = models.CharField(max_length=50, blank=True)
    state_name = models.CharField(max_length=50, blank=True)
    country_name = models.CharField(max_length=50, blank=True, default="India")
    contact_number = models.CharField(max_length=11, blank=True)
    pincode_number = models.CharField(max_length=6, blank=True)
    priority = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.buyer.id) + " - " + self.buyer.name + " - " + self.buyer.company_name + " - " + self.buyer.mobile_number

class BuyerDetails(models.Model):
    buyer = models.OneToOneField(Buyer)
    buyer_type = models.ForeignKey(BusinessType,blank=True, null=True)

    vat_tin = models.CharField(max_length=20, blank=True)
    cst = models.CharField(max_length=20, blank=True)

    customer_type = models.IntegerField(blank=True, default=0)

    # in number of pieces per month
    buying_capacity = models.IntegerField(blank=True, default=0)

    # in days
    purchase_duration = models.IntegerField(blank=True, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.buyer.id) + " - " + self.buyer.name + " - " + self.buyer.company_name + " - " + self.buyer.mobile_number

class BuyerInterest(models.Model):

    buyer = models.ForeignKey(Buyer)
    category = models.ForeignKey(Category)

    ## On a scale of 1 to 10
    scale = models.PositiveIntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.buyer.id) + " - " + self.buyer.name + " - " + self.category.name

class BuyerPurchasingState(models.Model):

    buyer = models.ForeignKey(Buyer)
    state = models.ForeignKey(State)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.buyer.id) + " - " + self.buyer.name + " - " + self.state.name

class BuyerBuysFrom(models.Model):

    buyer = models.ForeignKey(Buyer)
    business_type = models.ForeignKey(BusinessType,blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.buyer.id) + " - " + self.buyer.name + " - " + self.business_type.name

def validateBuyerData(buyer, oldbuyer, is_new):

    flag = 0

    if not "name" in buyer or buyer["name"]==None:
        flag = 1
        buyer["name"] = oldbuyer.name
    if not "company_name" in buyer or buyer["company_name"]==None:
        flag = 1
        buyer["company_name"] = oldbuyer.company_name
    if not "mobile_number" in buyer or buyer["mobile_number"]==None or not validate_mobile_number(buyer["mobile_number"]):
        flag = 1
        buyer["mobile_number"] = oldbuyer.mobile_number
    if not "email" in buyer or buyer["email"]==None or not validate_email(buyer["email"]):
        buyer["email"] = oldbuyer.email
        if is_new == 1:
            buyer["email"] = None
    if not "password" in buyer or buyer["password"]==None:
        buyer["password"] = oldbuyer.password
    if not "alternate_phone_number" in buyer or buyer["alternate_phone_number"]==None:
        buyer["alternate_phone_number"] = oldbuyer.alternate_phone_number
    if not "mobile_verification" in buyer or buyer["mobile_verification"]==None or not validate_bool(buyer["mobile_verification"]):
        buyer["mobile_verification"] = oldbuyer.mobile_verification
    if not "email_verification" in buyer or buyer["email_verification"]==None  or not validate_bool(buyer["email_verification"]):
        buyer["email_verification"] = oldbuyer.email_verification
    if not "gender" in buyer or buyer["gender"]:
        buyer["gender"] = oldbuyer.gender
    if not "password" in buyer or buyer["password"]:
        if is_new == 1:
            buyer["password"] = buyer["mobile_number"]
        else:
            buyer["password"] = oldbuyer.password

    if is_new == 1 and flag == 1:
        return False

    return True
    
def validateBuyerDetailsData(buyerdetails, oldbuyerdetails):

    if not "vat_tin" in buyerdetails or buyerdetails["vat_tin"]==None:
        buyerdetails["vat_tin"] = oldbuyerdetails.vat_tin
    if not "cst" in buyerdetails or buyerdetails["cst"]==None:
        buyerdetails["cst"] = oldbuyerdetails.cst
    if not "customer_type" in buyerdetails or buyerdetails["customer_type"]==None or not validate_buyer_customer_type(buyerdetails["customer_type"]):
        buyerdetails["customer_type"] = oldbuyerdetails.customer_type
    if not "buying_capacity" in buyerdetails or buyerdetails["buying_capacity"]==None  or not validate_integer(buyerdetails["purchase_duration"]):
        buyerdetails["buying_capacity"] = oldbuyerdetails.buying_capacity
    if not "purchase_duration" in buyerdetails or buyerdetails["purchase_duration"]==None or not validate_integer(buyerdetails["purchase_duration"]):
        buyerdetails["purchase_duration"] = oldbuyerdetails.purchase_duration


def validateBuyerAddressData(buyeraddress, oldbuyeraddress):

    if not "address" in buyeraddress or buyeraddress["address"]==None:
        buyeraddress["address"] = oldbuyeraddress.address_line
    if not "landmark" in buyeraddress or buyeraddress["landmark"]==None:
        buyeraddress["landmark"] = oldbuyeraddress.landmark
    if not "city" in buyeraddress or buyeraddress["city"]==None:
        buyeraddress["city"] = oldbuyeraddress.city_name
    if not "state" in buyeraddress or buyeraddress["state"]==None:
        buyeraddress["state"] = oldbuyeraddress.state_name
    if not "country" in buyeraddress or buyeraddress["country"]==None:
        buyeraddress["country"] = oldbuyeraddress.country_name
    if not "contact_number" in buyeraddress or buyeraddress["contact_number"]==None:
        buyeraddress["contact_number"] = oldbuyeraddress.contact_number
    if not "pincode" in buyeraddress or buyeraddress["pincode"]==None or not validate_pincode(buyeraddress["pincode"]):
        buyeraddress["pincode"] = oldbuyeraddress.pincode_number

def populateBuyer(buyerPtr, buyer):
    buyerPtr.name = buyer["name"]
    buyerPtr.company_name = buyer["company_name"]
    buyerPtr.mobile_number = buyer["mobile_number"]
    buyerPtr.email = buyer["email"]
    buyerPtr.password = buyer["password"]
    buyerPtr.alternate_phone_number = buyer["alternate_phone_number"]
    buyerPtr.mobile_verification = bool(buyer["mobile_verification"])
    buyerPtr.email_verification = bool(buyer["email_verification"])
    buyerPtr.gender = buyer["gender"]
    buyerPtr.password = buyer["password"]
    
def populateBuyerDetails(buyerDetailsPtr, buyerdetails):
    buyerDetailsPtr.cst = buyerdetails["cst"]
    buyerDetailsPtr.customer_type = int(buyerdetails["customer_type"])
    buyerDetailsPtr.buying_capacity = int(buyerdetails["buying_capacity"])
    buyerDetailsPtr.purchase_duration = int(buyerdetails["purchase_duration"])
    buyerDetailsPtr.vat_tin = buyerdetails["vat_tin"]

def populateBuyerAddress(buyerAddressPtr, buyeraddress):
    buyerAddressPtr.address_line = buyeraddress["address"]
    buyerAddressPtr.landmark = buyeraddress["landmark"]
    buyerAddressPtr.contact_number = buyeraddress["contact_number"]
    buyerAddressPtr.pincode_number = buyeraddress["pincode"]

    try:
        pincode = Pincode.objects.get(pincode=buyeraddress["pincode"])
        buyerAddressPtr.pincode = pincode
        buyerAddressPtr.city_name = pincode.city.name
        buyerAddressPtr.state_name = pincode.city.state.name
        buyerAddressPtr.country_name = pincode.city.state.country.name

    except Exception as e:
        buyerAddressPtr.city_name = buyeraddress["city"]
        buyerAddressPtr.state_name = buyeraddress["state"]
        buyerAddressPtr.country_name = "India"

def filterBuyer(buyerParameters):

    buyers = Buyer.objects.filter(delete_status=False).select_related('buyerdetails')

    if "buyersArr" in buyerParameters:
        buyers = buyers.filter(id__in=buyerParameters["buyersArr"])

    return buyers

def buyerEmailExists(email):
    buyerPtr = Buyer.objects.filter(email=email)

    if len(buyerPtr) > 0:
        return True

    return False

def buyerMobileNumberExists(mobileNumber):
    buyerPtr = Buyer.objects.filter(mobile_number=mobileNumber)

    if len(buyerPtr) > 0:
        return True

    return False

BuyerCustomerType = {
    0:{"display_value":"Average"},
    1:{"display_value":"Premium"},
    2:{"display_value":"Average and Premium"}
}

BuyerCustomerTypeValues = [0,1,2]

def validate_buyer_customer_type(x):
    if not validate_integer(x) or not (int(x) in BuyerCustomerTypeValues):
        return False
    return True