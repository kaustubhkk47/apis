from django.views.decorators.csrf import csrf_exempt
from scripts.utils import customResponse

@csrf_exempt
def invalid_request_details(request):

	return customResponse("4XX", {"error": "Invalid request url"})