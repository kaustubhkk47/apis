from django.views.decorators.csrf import csrf_exempt
from scripts.utils import customResponse, get_token_payload, getApiVersion, getPaginationParameters

from logistics.views import pincodeserviceability

@csrf_exempt
def pincode_serviceability_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	if request.method == "GET":

		parameters = populateLogisticsParameters(request, {}, version)

		return pincodeserviceability.get_pincode_serviceability_details(request,parameters)

	return customResponse("4XX", {"error": "Invalid request"})


def populateLogisticsParameters(request, parameters = {}, version = "0"):

	parameters = getPaginationParameters(request, parameters, 10, version)

	return parameters