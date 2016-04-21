from django.db import models

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
        return ""

class SellerDetails(models.Model):

    seller = models.OneToOneField(Seller)

    vat_tin = models.CharField(max_length=20, blank=True)
    cst = models.CharField(max_length=20, blank=True)

    account_holders_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=18)
    ifsc = models.CharField(max_length=11)

    pan = models.CharField(max_length=10, blank=True, null=False)
    name_on_pan = models.CharField(max_length=100, blank=True, null=False)
    dob_on_pan = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)

    pan_verification = models.BooleanField(default=0, blank=False, null=False)
    tin_verification = models.BooleanField(default=0, blank=False, null=False)

    def __unicode__(self):
        return self.seller.name
