from users.models.buyer import BuyerFireBaseToken, sendNotification
from orders.models.cart import filterCarts
from django.utils import timezone
from datetime import timedelta

def send_non_registered_buyer_notification():

	buyerFireBaseTokenPtr = BuyerFireBaseToken.objects.filter(buyer_id=None, delete_status=False)
	notification = {}
	notification["title"] = "Welcome to Wholdus"
	notification["body"] = "Register now for exclusive deals!"
	sendNotification(buyerFireBaseTokenPtr, notification = notification)

def send_buyer_welcome_notification():
	buyerFireBaseTokenPtr = BuyerFireBaseToken.objects.filter(buyer__created_at__gt=timezone.now() - timedelta(days=2), delete_status=False)
	notification = {}
	notification["title"] = "Welcome to Wholdus"
	notification["body"] = "5% cashback on first order. Only for 48 hrs!"
	sendNotification(buyerFireBaseTokenPtr, notification = notification)

def send_filled_cart_notification():

	cartPtr = filterCarts({})
	nowTime = timezone.now()
	cartPtr.filter(updated_at__gt=nowTime -  timedelta(hours=1, minutes=30), updated_at__lt=nowTime -  timedelta(minutes=30))

	for cartObj in cartPtr:
		notification = {}
		notification["title"] = "Wholdus"
		notification["body"] = "Difficulty in placing order? Call us for help"
		data = {}
		data["activity"] = "Help"
		sendNotification(cartObj.buyer.get_firebase_tokens(),notification = notification, data = data)