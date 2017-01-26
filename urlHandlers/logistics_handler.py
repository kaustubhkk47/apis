from django.views.decorators.csrf import csrf_exempt
from scripts.utils import customResponse, get_token_payload, getApiVersion, getPaginationParameters, getArrFromString, validate_bool

from logistics.views import pincodeserviceability

from .user_handler import populateAllUserIDParameters

@csrf_exempt
def pincode_serviceability_details(request, version = "0"):

	version = getApiVersion(request)

	parameters = populateLogisticsParameters(request, {}, version)

	if request.method == "GET":

		if parameters["isSeller"] == 0 and parameters["isInternalUser"] == 0 and parameters["isBuyer"] == 0:
			return customResponse(403, error_code = 8)
		
		return pincodeserviceability.get_pincode_serviceability_details(request,parameters)

	return customResponse(404, error_code = 7)


def populateLogisticsParameters(request, parameters = {}, version = "0"):

	parameters = getPaginationParameters(request, parameters, 10, version)
	parameters = populateAllUserIDParameters(request, parameters, version)

	pincodeCode = request.GET.get("pincode_code", "")
	if pincodeCode != "" and pincodeCode != None:
		parameters["pincodesCodesArr"] = getArrFromString(pincodeCode)

	pincodeID = request.GET.get("pincodeID", "")
	if pincodeID != "" and pincodeID != None:
		parameters["pincodesArr"] = getArrFromString(pincodeID)

	logisticsPartnerID = request.GET.get("logisticspartnerID", "")
	if logisticsPartnerID != "" and logisticsPartnerID != None:
		parameters["logisticsPartnersArr"] = getArrFromString(logisticsPartnerID)

	regularDeliveryAvailable = request.GET.get("regular_delivery_available", "")
	if validate_bool(regularDeliveryAvailable):
		parameters["regular_delivery_available"] = int(regularDeliveryAvailable)

	regularPickupAvailable = request.GET.get("regular_pickup_available", "")
	if validate_bool(regularPickupAvailable):
		parameters["regular_pickup_available"] = int(regularPickupAvailable)

	codAvailable = request.GET.get("cod_available", "")
	if validate_bool(codAvailable):
		parameters["cod_available"] = int(codAvailable)

	return parameters