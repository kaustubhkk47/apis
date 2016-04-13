from __future__ import unicode_literals

from django.db import models

class Buyer(models.Model):
    name = models.CharField(max_length=200, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    mobile_number = models.CharField(max_length=11, blank=False, db_index=True)
    email = models.EmailField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=False)
    alternate_phone_number = models.CharField(max_length=11, blank=True)
    mobile_verification = models.BooleanField(default=False)
    email_verification = models.BooleanField(default=False)
    gender = models.CharField(max_length=10, blank=True)

    def __unicode__(self):
        return self.name

class Seller(models.Model):
    name = models.CharField(max_length=200, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    mobile_number = models.CharField(max_length=11, blank=False, db_index=True)
    email = models.EmailField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=False)
    alternate_phone_number = models.CharField(max_length=11, blank=True)
    mobile_verification = models.BooleanField(default=False)
    email_verification = models.BooleanField(default=False)

    def __unicode__(self):
        return self.company_name

class InternalUser(models.Model):
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(max_length=255, blank=False, unique=True)
    mobile_number = models.CharField(max_length=11, blank=True)
    password = models.CharField(max_length=255, blank=False)

    def __unicode__(self):
        return self.name
