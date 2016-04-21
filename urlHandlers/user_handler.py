from django.views.decorators.csrf import csrf_exempt

from users.views import user

@csrf_exempt
def user_details(request):

	if request.method == "GET":
		return user.get_user_details(request)

	return customResponse("4XX", {"error": "Invalid request"})
