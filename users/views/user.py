from scripts.utils import customResponse, closeDBConnection

from ..models.buyer import Buyer, BuyerAddress
from ..models.seller import Seller, SellerAddress
from ..serializers.buyer import get_buyer_details
from ..serializers.seller import get_seller_details

def get_user_details(request):
	try:
		buyers = Buyer.objects.all()
		
		sellers = Seller.objects.all()

		buyer_details = get_buyer_details(buyers)
		seller_details = get_seller_details(sellers)

		all_users = {
			"buyers" : buyer_details,
			"sellers" : seller_details
		}

		return customResponse("2XX", {"users": all_users})
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid request"})