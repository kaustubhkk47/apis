from ..models.smssent import *
from scripts.utils import validate_integer, closeDBConnection, customResponse

import logging
log = logging.getLogger("django")

def post_delivery_report(request):
	try:
		delivery_report = request.POST
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(delivery_report) or not "customID" in delivery_report or not validate_integer(delivery_report["customID"]):
		return customResponse("4XX", {"error": "Invalid data for delivery report sent"})

	smsSentPtr = SMSSent.objects.filter(id=int(delivery_report["customID"]))

	if len(smsSentPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for delivery report sent"})

	smsSentPtr = smsSentPtr[0]

	if not validateSmsSentData(delivery_report):
		return customResponse("4XX", {"error": "Invalid data sent"})

	try:
		smsSentPtr.delivery_status = delivery_report["status"]
		if delivery_report["status"] == "D":
			smsSentPtr.delivered = 1
			smsSentPtr.delivered_time = delivery_report["datetime"]

		smsSentPtr.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "could not update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"success": "updated successfully"})
