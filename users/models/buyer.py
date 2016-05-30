from django.db import models

#Make changes in model, validate, populate and serializer 

class Buyer(models.Model):
    name = models.CharField(max_length=200, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    mobile_number = models.CharField(max_length=11, blank=False, db_index=True)
    email = models.EmailField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    alternate_phone_number = models.CharField(max_length=11, blank=True)
    mobile_verification = models.BooleanField(default=False)
    email_verification = models.BooleanField(default=False)
    gender = models.CharField(max_length=10, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    delete_status = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

class BuyerAddress(models.Model):
    buyer = models.ForeignKey(Buyer)

    address = models.CharField(max_length=255, blank=True, null=False)
    landmark = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True, default="India")
    contact_number = models.CharField(max_length=11, blank=True)
    pincode = models.CharField(max_length=6, blank=True)
    priority = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.buyer.name

class BuyerDetails(models.Model):
    buyer = models.OneToOneField(Buyer)

    vat_tin = models.CharField(max_length=20, blank=True)
    cst = models.CharField(max_length=20, blank=True)

    buyer_interest = models.TextField(blank = True)
    customer_type = models.CharField(max_length=20, blank=True)
    buying_capacity = models.CharField(max_length=20, blank=True)
    purchase_duration = models.CharField(max_length=20, blank=True)
    buys_from = models.CharField(max_length=20, blank=True)
    purchasing_states = models.TextField(blank = True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.buyer.name

def validateBuyerData(buyer, oldbuyer, is_new):

    flag = 0

    if not "name" in buyer or buyer["name"]==None:
        flag = 1
        buyer["name"] = oldbuyer.name
    if not "company_name" in buyer or buyer["company_name"]==None:
        flag = 1
        buyer["company_name"] = oldbuyer.company_name
    if not "mobile_number" in buyer or buyer["mobile_number"]==None:
        flag = 1
        buyer["mobile_number"] = oldbuyer.mobile_number
    if not "email" in buyer or buyer["email"]==None:
        buyer["email"] = oldbuyer.email
    if not "password" in buyer or buyer["password"]==None:
        buyer["password"] = oldbuyer.password
    if not "alternate_phone_number" in buyer or buyer["alternate_phone_number"]==None:
        buyer["alternate_phone_number"] = oldbuyer.alternate_phone_number
    if not "mobile_verification" in buyer or buyer["mobile_verification"]==None:
        buyer["mobile_verification"] = oldbuyer.mobile_verification
    if not "email_verification" in buyer or buyer["email_verification"]==None:
        buyer["email_verification"] = oldbuyer.email_verification
    if not "gender" in buyer or buyer["gender"]:
        buyer["gender"] = oldbuyer.gender

    if is_new == 1 and flag == 1:
        return False

    return True


    
def validateBuyerDetailsData(buyerdetails, oldbuyerdetails):

    if not "vat_tin" in buyerdetails or buyerdetails["vat_tin"]==None:
        buyerdetails["vat_tin"] = oldbuyerdetails.vat_tin
    if not "cst" in buyerdetails or buyerdetails["cst"]==None:
        buyerdetails["cst"] = oldbuyerdetails.cst
    if not "buyer_interest" in buyerdetails or buyerdetails["buyer_interest"]==None:
        buyerdetails["buyer_interest"] = oldbuyerdetails.buyer_interest
    if not "customer_type" in buyerdetails or buyerdetails["customer_type"]==None:
        buyerdetails["customer_type"] = oldbuyerdetails.customer_type
    if not "buying_capacity" in buyerdetails or buyerdetails["buying_capacity"]==None:
        buyerdetails["buying_capacity"] = oldbuyerdetails.buying_capacity
    if not "purchase_duration" in buyerdetails or buyerdetails["purchase_duration"]==None:
        buyerdetails["purchase_duration"] = oldbuyerdetails.purchase_duration
    if not "buys_from" in buyerdetails or buyerdetails["buys_from"]==None:
        buyerdetails["buys_from"] = oldbuyerdetails.buys_from
    if not "purchasing_states" in buyerdetails or buyerdetails["purchasing_states"]==None:
        buyerdetails["purchasing_states"] = oldbuyerdetails.purchasing_states 


def validateBuyerAddressData(buyeraddress, oldbuyeraddress):

    if not "address" in buyeraddress or buyeraddress["address"]==None:
        buyeraddress["address"] = oldbuyeraddress.address
    if not "landmark" in buyeraddress or buyeraddress["landmark"]==None:
        buyeraddress["landmark"] = oldbuyeraddress.landmark
    if not "city" in buyeraddress or buyeraddress["city"]==None:
        buyeraddress["city"] = oldbuyeraddress.city
    if not "state" in buyeraddress or buyeraddress["state"]==None:
        buyeraddress["state"] = oldbuyeraddress.state
    if not "country" in buyeraddress or buyeraddress["country"]==None:
        buyeraddress["country"] = oldbuyeraddress.country
    if not "contact_number" in buyeraddress or buyeraddress["contact_number"]==None:
        buyeraddress["contact_number"] = oldbuyeraddress.contact_number
    if not "pincode" in buyeraddress or buyeraddress["pincode"]==None:
        buyeraddress["pincode"] = oldbuyeraddress.pincode

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
    
def populateBuyerDetails(buyerDetailsPtr, buyerdetails):
    buyerDetailsPtr.cst = buyerdetails["cst"]
    buyerDetailsPtr.buyer_interest = buyerdetails["buyer_interest"]
    buyerDetailsPtr.customer_type = buyerdetails["customer_type"]
    buyerDetailsPtr.buying_capacity = buyerdetails["buying_capacity"]
    buyerDetailsPtr.purchase_duration = buyerdetails["purchase_duration"]
    buyerDetailsPtr.buys_from = buyerdetails["buys_from"]
    buyerDetailsPtr.purchasing_states = buyerdetails["purchasing_states"]
    buyerDetailsPtr.vat_tin = buyerdetails["vat_tin"]

def populateBuyerAddress(buyerAddressPtr, buyeraddress):
    buyerAddressPtr.address = buyeraddress["address"]
    buyerAddressPtr.landmark = buyeraddress["landmark"]
    buyerAddressPtr.city = buyeraddress["city"]
    buyerAddressPtr.state = buyeraddress["state"]
    buyerAddressPtr.country = buyeraddress["country"]
    buyerAddressPtr.contact_number = buyeraddress["contact_number"]
    buyerAddressPtr.pincode = buyeraddress["pincode"]

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