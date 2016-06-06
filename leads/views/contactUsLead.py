from scripts.utils import *
import json

from ..models.contactUsLead import ContactUsLead, validateContactUsLeadData, populateContactUsLead
from ..serializers.contactUsLead import *

def get_contactus_leads(request):
	try:
		contactusLeads = ContactUsLead.objects.all()
		closeDBConnection()
		body = parseContactUsLeads(contactusLeads)
		statusCode = "2XX"
		response = {"contactus_leads": body}
	except Exception, e:
		statusCode = "4XX"
		response = {"error": "Invalid request"}
	return customResponse(statusCode, response)

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
			from_email = "Wholdus Info <info@wholdus.com>"
			bcc = ["manish@wholdus.com"]
			create_email(mail_template_file,mail_dict,subject,from_email,to,bcc=bcc)

		return customResponse("2XX", {"contactus_lead" : serialize_contactus_lead(newcontactUsLead)})

def update_contactus_lead(request):
	try:
		requestbody = request.body.decode("utf-8")
		contactusLead = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(contactusLead) or not "contactusleadID" in contactusLead or contactusLead["contactusleadID"]==None:
		return customResponse("4XX", {"error": "Id for contactus lead not sent"})

	contactusLeadPtr = ContactUsLead.objects.filter(id=int(contactusLead["contactusleadID"]))

	if len(contactusLeadPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for contactus lead sent"})

	contactusLeadPtr = contactusLeadPtr[0]

	if not validateContactUsLeadData(contactusLead, contactusLeadPtr, 0):
		return customResponse("4XX", {"error": "Invalid data for contactus lead sent"})

	try:
		populateContactUsLead(contactusLeadPtr, contactusLead)
		contactusLeadPtr.save()

	except Exception as e:
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to update contactus lead"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"contactus_lead" : serialize_contactus_lead(contactusLeadPtr)})