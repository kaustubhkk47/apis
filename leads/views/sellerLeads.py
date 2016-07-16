from scripts.utils import *
import json

from ..models.sellerLeads import *
from ..serializers.sellerLeads import *

import logging
log = logging.getLogger("django")

def get_seller_leads(request, sellerLeadParameters):
	try:
		sellerLeads = SellerLeads.objects.all()

		if "sellerLeadsArr" in sellerLeadParameters:
			sellerLeads = sellerLeads.filter(id__in=sellerLeadParameters["sellerLeadsArr"])

		if "statusArr" in sellerLeadParameters:
			sellerLeads = sellerLeads.filter(status__in=sellerLeadParameters["statusArr"])
			
		closeDBConnection()
		body = parseSellerLeads(sellerLeads)
		statusCode = "2XX"
		response = {"seller_leads": body}
	except Exception, e:
		log.critical(e)
		statusCode = "4XX"
		response = {"error": "Invalid request"}
	return customResponse(statusCode, response)
	

def post_new_seller_lead(request):
	try:
		requestbody = request.body.decode("utf-8")
		sellerLead = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(sellerLead) or not validateSellerLeadData(sellerLead, SellerLeads(), 1):
		return customResponse("4XX", {"error": "Invalid data for seller lead sent"})

	try:
		newSellerLead = SellerLeads()

		populateSellerLead(newSellerLead, sellerLead)

		newSellerLead.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"seller_lead" : serialize_seller_lead(newSellerLead)})

def update_seller_lead(request):
	try:
		requestbody = request.body.decode("utf-8")
		sellerLead = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(sellerLead) or not "sellerleadID" in sellerLead or not validate_integer(sellerLead["sellerleadID"]):
		return customResponse("4XX", {"error": "Id for seller lead not sent"})

	sellerLeadPtr = SellerLeads.objects.filter(id=int(sellerLead["sellerleadID"]))

	if len(sellerLeadPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for seller lead sent"})

	sellerLeadPtr = sellerLeadPtr[0]

	if not validateSellerLeadData(sellerLead, sellerLeadPtr, 0):
		return customResponse("4XX", {"error": "Invalid data for seller lead sent"})

	try:
		populateSellerLead(sellerLeadPtr, sellerLead)
		sellerLeadPtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to update seller lead"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"seller_lead" : serialize_seller_lead(sellerLeadPtr)})