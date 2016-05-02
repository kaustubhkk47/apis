from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string
import json

from ..models.buyerLeads import BuyerLeads, validateBuyerLeadData, populateBuyerLead
from ..serializers.buyerLeads import serialize_buyer_lead

def post_new_buyer_lead(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyerLead = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyerLead) or not validateBuyerLeadData(buyerLead, BuyerLeads(), 1):
		return customResponse("4XX", {"error": "Invalid data for buyer lead sent"})

	try:
		newBuyerLead = BuyerLeads()

		populateBuyerLead(newBuyerLead, buyerLead)

		newBuyerLead.save()
	except Exception as e:
		print e
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer_lead" : serialize_buyer_lead(newBuyerLead)})