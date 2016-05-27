from scripts.utils import *
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
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()

		if("email" in contactUsLead and contactUsLead["email"]):
			mail_template_file = "leads/contactus_lead.html"
			mail_dict = {}
			subject = "We at Wholdus have received your request"
			to = [contactUsLead["email"]]
			from_email = "info@wholdus.com"
			create_email(mail_template_file,mail_dict,subject,from_email,to)

		return customResponse("2XX", {"contactUs_lead" : serialize_contactus_lead(newcontactUsLead)})