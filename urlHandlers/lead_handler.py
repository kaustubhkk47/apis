from django.views.decorators.csrf import csrf_exempt
from scripts.utils import customResponse, get_token_payload, getArrFromString, getApiVersion
from leads.views import buyerLeads,contactUsLead, sellerLeads

from .user_handler import populateInternalUserIDParameters

@csrf_exempt
def buyer_leads(request, version = "0"):

	version = getApiVersion(request)

	parameters = getBuyerLeadParameters(request, {}, version)

	if request.method == "GET":

		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)

		return buyerLeads.get_buyer_leads(request,parameters)
	if request.method == "POST":
		return buyerLeads.post_new_buyer_lead(request)
	elif request.method == "PUT":
		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)
		return buyerLeads.update_buyer_lead(request)

	return customResponse(404, error_code = 7)

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

	version = getApiVersion(request)

	parameters = getSellerLeadParameters(request, {}, version)

	if request.method == "GET":

		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)

		return sellerLeads.get_seller_leads(request,parameters)
	elif request.method == "POST":
		return sellerLeads.post_new_seller_lead(request)
	elif request.method == "PUT":
		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)
		return sellerLeads.update_seller_lead(request)

	return customResponse(404, error_code = 7)

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

	version = getApiVersion(request)

	parameters = getContactUsLeadParameters(request, {}, version)

	if request.method == "GET":

		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)

		return contactUsLead.get_contactus_leads(request,parameters)
	if request.method == "POST":
		return contactUsLead.post_new_contactus_lead(request)
	elif request.method == "PUT":
		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)
		return contactUsLead.update_contactus_lead(request)

	return customResponse(404, error_code = 7)

def getContactUsLeadParameters(request, parameters = {}, version = "0"):

	status = request.GET.get("status", "")
	if status != "":
		parameters["statusArr"] = getArrFromString(status)

	contactUsLeadID = request.GET.get("contactusleadID", "")
	if contactUsLeadID != "":
		parameters["contactUsLeadsArr"] = getArrFromString(contactUsLeadID)

	parameters = populateInternalUserIDParameters(request, parameters, version)

	return parameters