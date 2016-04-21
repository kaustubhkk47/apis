from scripts.utils import customResponse, closeDBConnection

from ..models.buyer import Buyer, BuyerAddress
from ..serializers.buyer import parse_buyer

def get_buyer_details(request,buyersArr=[]):
	try:
		if len(buyersArr)==0:
			buyers = Buyer.objects.all().select_related('buyerdetails')
			closeDBConnection()
		else:
			buyers = Buyer.objects.filter(id__in=buyersArr).select_related('buyerdetails')
			closeDBConnection()

		response = {
			"buyers" : parse_buyer(buyers)
		}

		return customResponse("2XX", response)
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid request"})