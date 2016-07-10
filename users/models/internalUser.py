from django.db import models

import jwt as JsonWebToken
import settings

#Make changes in model, validate, populate and serializer 

class InternalUser(models.Model):
	name = models.CharField(max_length=200, blank=True)
	email = models.EmailField(max_length=255, blank=False, unique=True)
	mobile_number = models.CharField(max_length=11, blank=True)
	password = models.CharField(max_length=255, blank=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	linkedin_profile_link = models.TextField(blank=True,null=True)
	facebook_profile_link = models.TextField(blank=True,null=True)

	def __unicode__(self):
		return str(self.id) + " - " + self.name

def filterInternalUser(parameters = {}):

	internalUsers = InternalUser.objects.all()

	if "internalusersArr" in parameters:
		internalUsers = internalUsers.filter(id__in=parameters["internalusersArr"])

	return internalUsers

def getInternalUserToken(internaluser):
	tokenPayload = {
		"user": "internaluser",
		"internaluserID": internaluser.id,
	}
	encoded = JsonWebToken.encode(tokenPayload, settings.SECRET_KEY, algorithm='HS256')
	return encoded.decode("utf-8")
