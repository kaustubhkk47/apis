from django.views.decorators.csrf import csrf_exempt
from scripts.utils import customResponse

from general.views import smssent

@csrf_exempt
def invalid_request_details(request):

	return customResponse(404, error_code = 7)

@csrf_exempt
def delivery_report_details(request, version = "0"):

	if request.method == "POST":
	
		return smssent.post_delivery_report(request)

	return customResponse(404, error_code = 7)