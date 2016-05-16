from django.views.decorators.csrf import csrf_exempt
from scripts.utils import customResponse, get_token_payload
from leads.views import buyerLeads,contactUsLead

@csrf_exempt
def buyer_leads(request):

	if request.method == "POST":
		return buyerLeads.post_new_buyer_lead(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def contactus_leads(request):

	if request.method == "POST":
		return contactUsLead.post_new_contactus_lead(request)

	return customResponse("4XX", {"error": "Invalid request"})