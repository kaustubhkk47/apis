from django.views.decorators.csrf import csrf_exempt
from scripts.utils import customResponse, get_token_payload, getArrFromString
from leads.views import buyerLeads,contactUsLead, sellerLeads

@csrf_exempt
def buyer_leads(request):

	if request.method == "GET":

		buyerLeadParameters = {}

		status = request.GET.get("status", "")
		buyerLeadID = request.GET.get("buyerleadID", "")
		accessToken = request.GET.get("access_token", "")

		tokenPayload = get_token_payload(accessToken, "internaluserID")
		buyerLeadParameters["isInternalUser"] = 0
		if "internaluserID" in tokenPayload and tokenPayload["internaluserID"]!=None:
			buyerLeadParameters["internalusersArr"] = [tokenPayload["internaluserID"]]
			buyerLeadParameters["isInternalUser"] = 1

		if status != "":
			buyerLeadParameters["statusArr"] = getArrFromString(status)

		if buyerLeadID != "":
			buyerLeadParameters["buyerLeadsArr"] = getArrFromString(buyerLeadID)

		return buyerLeads.get_buyer_leads(request,buyerLeadParameters)
	if request.method == "POST":
		return buyerLeads.post_new_buyer_lead(request)
	elif request.method == "PUT":
		return buyerLeads.update_buyer_lead(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def seller_leads(request):

	if request.method == "GET":

		sellerLeadParameters = {}

		status = request.GET.get("status", "")
		sellerLeadID = request.GET.get("sellerleadID", "")
		accessToken = request.GET.get("access_token", "")

		tokenPayload = get_token_payload(accessToken, "internaluserID")
		sellerLeadParameters["isInternalUser"] = 0
		if "internaluserID" in tokenPayload and tokenPayload["internaluserID"]!=None:
			sellerLeadParameters["internalusersArr"] = [tokenPayload["internaluserID"]]
			sellerLeadParameters["isInternalUser"] = 1

		if status != "":
			sellerLeadParameters["statusArr"] = getArrFromString(status)

		if sellerLeadID != "":
			sellerLeadParameters["sellerLeadsArr"] = getArrFromString(sellerLeadID)

		return sellerLeads.get_seller_leads(request,sellerLeadParameters)
	elif request.method == "POST":
		return sellerLeads.post_new_seller_lead(request)
	elif request.method == "PUT":
		return sellerLeads.update_seller_lead(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def contactus_leads(request):

	if request.method == "GET":

		contactUsLeadParameters = {}

		status = request.GET.get("status", "")
		contactUsLeadID = request.GET.get("contactusleadID", "")
		accessToken = request.GET.get("access_token", "")

		tokenPayload = get_token_payload(accessToken, "internaluserID")
		contactUsLeadParameters["isInternalUser"] = 0
		if "internaluserID" in tokenPayload and tokenPayload["internaluserID"]!=None:
			contactUsLeadParameters["internalusersArr"] = [tokenPayload["internaluserID"]]
			contactUsLeadParameters["isInternalUser"] = 1

		if status != "":
			contactUsLeadParameters["statusArr"] = getArrFromString(status)

		if contactUsLeadID != "":
			contactUsLeadParameters["contactUsLeadsArr"] = getArrFromString(contactUsLeadID)
		return contactUsLead.get_contactus_leads(request,contactUsLeadParameters)
	if request.method == "POST":
		return contactUsLead.post_new_contactus_lead(request)
	elif request.method == "PUT":
		return contactUsLead.update_contactus_lead(request)

	return customResponse("4XX", {"error": "Invalid request"})