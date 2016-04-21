from django.db import models

## Whenever making any changes, add fields to models, serializers and validation

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

    def __unicode__(self):
        return self.address

class BuyerDetails(models.Model):
    buyer = models.OneToOneField(Buyer)

    vat_tin = models.CharField(max_length=20, blank=True)
    cst = models.CharField(max_length=20, blank=True)

    buyer_interest = models.TextField(blank = True)
    customer_type = models.CharField(max_length=20, blank=True)
    buying_capacity = models.CharField(max_length=20, blank=True)
    buys_from = models.CharField(max_length=20, blank=True)
    purchasing_states = models.TextField(blank = True)

    def __unicode__(self):
        return self.buyer.name
