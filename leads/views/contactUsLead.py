from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string
import json

from ..models.contactUsLead import ContactUsLead, validateContactUsLeadData, populateContactUsLead
from ..serializers.contactUsLead import serialize_contactus_lead

def post_new_contactus_lead(request):
	try:
		requestbody = request.body.decode("utf-8")
		contactUsLead = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(contactUsLead) or not validateContactUsLeadData(contactUsLead, ContactUsLead(), 1):
		return customResponse("4XX", {"error": "Invalid data for contactUs lead sent"})

	try:
		newcontactUsLead = ContactUsLead()

		populateContactUsLead(newcontactUsLead, contactUsLead)

		newcontactUsLead.save()
	except Exception as e:
		print e
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"contactUs_lead" : serialize_contactus_lead(newcontactUsLead)})