from ..models.smssent import *
from scripts.utils import validate_integer, closeDBConnection, customResponse

import logging
log = logging.getLogger("django")

def post_delivery_report(request):
	try:
		delivery_report = request.POST
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(delivery_report) or not "customID" in delivery_report or not validate_integer(delivery_report["customID"]):
		return customResponse(400, error_code=5,  error_details="Invalid data for delivery report sent")

	smsSentPtr = SMSSent.objects.filter(id=int(delivery_report["customID"]))

	if len(smsSentPtr) == 0:
		return customResponse(400, error_code=6,  error_details="Invalid id for delivery report sent")

	smsSentPtr = smsSentPtr[0]

	if not validateSmsSentData(delivery_report):
		return customResponse(400, error_code=5)

	try:
		smsSentPtr.delivery_status = delivery_report["status"]
		if delivery_report["status"] == "D":
			smsSentPtr.delivered = 1
			smsSentPtr.delivered_time = delivery_report["datetime"]

		smsSentPtr.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"success": "updated successfully"})
