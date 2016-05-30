from scripts.utils import *
import json

from ..models.sellerLeads import *
from ..serializers.sellerLeads import *

def get_seller_leads(request):
	try:
		sellerLeads = SellerLeads.objects.all()
		closeDBConnection()
		body = parseSellerLeads(sellerLeads)
		statusCode = "2XX"
		response = {"seller_leads": body}
	except Exception, e:
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
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"seller_lead" : serialize_seller_lead(newSellerLead)})