from scripts.utils import customResponse, closeDBConnection
from ..models.seller import Seller, SellerAddress
from ..serializers.seller import parse_seller

def get_seller_details(request,sellersArr=[]):
	try:
		if len(sellersArr)==0:
			sellers = Seller.objects.filter(delete_status=False).select_related('sellerdetails')
			closeDBConnection()
		else:
			sellers = Seller.objects.filter(delete_status=False,id__in=sellersArr).select_related('sellerdetails')
			closeDBConnection()

		response = {
			"sellers" : parse_seller(sellers)
		}

		return customResponse("2XX", response)
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid request"})