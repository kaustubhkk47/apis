from django.views.decorators.csrf import csrf_exempt
from scripts.utils import customResponse

from general.views import smssent
from general.views import faqs

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