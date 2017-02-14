from django.views.decorators.csrf import csrf_exempt
from scripts.utils import customResponse, getPaginationParameters, validate_bool, getArrFromString

from general.views import smssent
from general.views import faqs
from general.views import configuration
from general.views import marketing_contacts

from .user_handler import populateInternalUserIDParameters

@csrf_exempt
def invalid_request_details(request):

	return customResponse(404, error_code = 7)

@csrf_exempt
def delivery_report_details(request, version = "0"):

	if request.method == "POST":
	
		return smssent.post_delivery_report(request)

	return customResponse(404, error_code = 7)

@csrf_exempt
def faq_details(request, version = "0"):

	if request.method == "GET":
	
		return faqs.get_faq_details(request)

	return customResponse(404, error_code = 7)

@csrf_exempt
def privacy_policy_details(request, version = "0"):

	if request.method == "GET":
	
		return faqs.get_privacy_policy_details(request)

	return customResponse(404, error_code = 7)

@csrf_exempt
def about_us_details(request, version = "0"):

	if request.method == "GET":
	
		return faqs.get_about_us_details(request)

	return customResponse(404, error_code = 7)

@csrf_exempt
def terms_and_conditions_details(request, version = "0"):

	if request.method == "GET":
	
		return faqs.get_terms_and_conditions_details(request)

	return customResponse(404, error_code = 7)

@csrf_exempt
def cart_min_value_details(request, version = "0"):

	if request.method == "GET":
	
		return configuration.get_cart_min_value_details(request)

	return customResponse(404, error_code = 7)


@csrf_exempt
def marketing_contact_details(request, version="0"):

	parameters = populateMarketingContactsParameters(request, {}, version)

	if request.method == "GET":
		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)
		return marketing_contacts.get_marketing_contact_details(request, parameters)
	elif request.method == "POST":
		return marketing_contacts.post_new_marketing_contact(request, parameters)
	elif request.method == "PUT":
		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)
		return marketing_contacts.update_marketing_contact(request, parameters)

	return customResponse(404, error_code=7)

def populateMarketingContactsParameters(request, parameters = {}, version = "0"):
	parameters = populateInternalUserIDParameters(request, parameters, version)
	parameters = getPaginationParameters(request, parameters, 50)

	newContacts = request.GET.get("new_contacts", "")
	if newContacts != "" and validate_bool(newContacts):
		parameters["new_contacts"] = newContacts
	else:
		parameters["new_contacts"] = 1

	marketingContactID = request.GET.get("marketingcontactID", "")
	if marketingContactID != "" and marketingContactID != None:
		parameters["marketingContactsArr"] = getArrFromString(marketingContactID)

	return parameters

@csrf_exempt
def buyer_app_link_details(request, version="0"):

	return marketing_contacts.redirect_to_buyer_app(request, {})