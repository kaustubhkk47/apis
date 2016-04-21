from scripts.utils import customResponse, closeDBConnection

from ..models.buyer import Buyer, BuyerAddress
from ..models.seller import Seller, SellerAddress
from ..serializers.buyer import parse_buyer
from ..serializers.seller import parse_seller

def get_user_details(request):
	try:
		buyers = Buyer.objects.all().select_related('buyerdetails')
		sellers = Seller.objects.all().select_related('sellerdetails')

		closeDBConnection()

		response = {
			"buyers" : parse_buyer(buyers),
			"sellers" : parse_seller(sellers)
		}

		return customResponse("2XX", {"users": response})
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid request"})