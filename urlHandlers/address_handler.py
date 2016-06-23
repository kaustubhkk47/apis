from django.views.decorators.csrf import csrf_exempt
from scripts.utils import customResponse, get_token_payload

from address.views import state

@csrf_exempt
def state_details(request):

	if request.method == "GET":

		stateParameters = populateParameters(request)

		return state.get_state_details(request,stateParameters)

	return customResponse("4XX", {"error": "Invalid request"})


def populateParameters(request):

	parameters = {}

	return parameters