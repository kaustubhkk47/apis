from django.views.decorators.csrf import csrf_exempt
from scripts.utils import customResponse, get_token_payload, getArrFromString
from leads.views import buyerLeads,contactUsLead, sellerLeads

from .user_handler import populateInternalUserIDParameters

@csrf_exempt
def buyer_leads(request, version = "0"):

	if request.method == "GET":

		buyerLeadParameters = getBuyerLeadParameters(request, {}, version)

		return buyerLeads.get_buyer_leads(request,buyerLeadParameters)
	if request.method == "POST":
		return buyerLeads.post_new_buyer_lead(request)
	elif request.method == "PUT":
		return buyerLeads.update_buyer_lead(request)

	return customResponse("4XX", {"error": "Invalid request"})

def getBuyerLeadParameters(request, parameters = {}, version = "0"):

	status = request.GET.get("status", "")
	if status != "":
		parameters["statusArr"] = getArrFromString(status)

	buyerLeadID = request.GET.get("buyerleadID", "")
	if buyerLeadID != "":
		parameters["buyerLeadsArr"] = getArrFromString(buyerLeadID)

	parameters = populateInternalUserIDParameters(request, parameters, version)

	return parameters

@csrf_exempt
def seller_leads(request, version = "0"):

	if request.method == "GET":

		sellerLeadParameters = getSellerLeadParameters(request, {}, version)

		return sellerLeads.get_seller_leads(request,sellerLeadParameters)
	elif request.method == "POST":
		return sellerLeads.post_new_seller_lead(request)
	elif request.method == "PUT":
		return sellerLeads.update_seller_lead(request)

	return customResponse("4XX", {"error": "Invalid request"})

def getSellerLeadParameters(request, parameters = {}, version = "0"):

	status = request.GET.get("status", "")
	if status != "":
		parameters["statusArr"] = getArrFromString(status)

	sellerLeadID = request.GET.get("sellerleadID", "")
	if sellerLeadID != "":
		parameters["sellerLeadsArr"] = getArrFromString(sellerLeadID)

	parameters = populateInternalUserIDParameters(request, parameters, version)

	return parameters

@csrf_exempt
def contactus_leads(request, version = "0"):

	if request.method == "GET":

		contactUsLeadParameters = getContactUsLeadParameters(request, {}, version)

		contactUsLeadID = request.GET.get("contactusleadID", "")

		if contactUsLeadID != "":
			contactUsLeadParameters["contactUsLeadsArr"] = getArrFromString(contactUsLeadID)

		return contactUsLead.get_contactus_leads(request,contactUsLeadParameters)
	if request.method == "POST":
		return contactUsLead.post_new_contactus_lead(request)
	elif request.method == "PUT":
		return contactUsLead.update_contactus_lead(request)

	return customResponse("4XX", {"error": "Invalid request"})

def getContactUsLeadParameters(request, parameters = {}, version = "0"):

	status = request.GET.get("status", "")
	if status != "":
		parameters["statusArr"] = getArrFromString(status)

	contactUsLeadID = request.GET.get("contactusleadID", "")
	if contactUsLeadID != "":
		contactUsLeadParameters["contactUsLeadsArr"] = getArrFromString(contactUsLeadID)

	parameters = populateInternalUserIDParameters(request, parameters, version)

	return parameters