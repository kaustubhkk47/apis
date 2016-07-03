from django.views.decorators.csrf import csrf_exempt
from scripts.utils import customResponse, get_token_payload

from address.views import state

@csrf_exempt
def state_details(request):

	if request.method == "GET":

		parameters = populateAddressParameters(request)

		return state.get_state_details(request,parameters)

	return customResponse("4XX", {"error": "Invalid request"})


def populateAddressParameters(request, parameters = {}):

	return parameters