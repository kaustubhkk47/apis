from django.views.decorators.csrf import csrf_exempt
from scripts.utils import customResponse, get_token_payload, getApiVersion

from address.views import state

from .logistics_handler import populateLogisticsParameters

@csrf_exempt
def state_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	parameters = populateAddressParameters(request, {}, version)

	if request.method == "GET":

		return state.get_state_details(request,parameters)

	return customResponse("4XX", {"error": "Invalid request"})


def populateAddressParameters(request, parameters = {}, version = "0"):

	return parameters

@csrf_exempt
def pincode_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	if request.method == "GET":

		return state.get_state_details(request,parameters)

	return customResponse("4XX", {"error": "Invalid request"})