from users.models.buyer import *
def create_buyer_address_history():
	buyers = Buyer.objects.all()
	for buyerPtr in buyers:
		buyerAddressPtr = BuyerAddress.objects.filter(buyer=buyerPtr)
		if len(buyerAddressPtr) == 0:
			buyeraddress["address"] = ""
			buyeraddress["landmark"] = ""
			buyeraddress["contact_number"] = ""
			buyeraddress["pincode"] = ""
			buyeraddress["city"] = ""
			buyeraddress["state"] = ""
			buyerAddressPtr = BuyerAddress(buyer=buyerPtr)
			populateBuyerAddress(buyerAddressPtr, buyeraddress)
		else:
			buyerAddressPtr = buyerAddressPtr[0]

		newBuyerAddressHistory = BuyerAddressHistory()
		newBuyerAddressHistory.populateFromBuyerAddress(buyerAddressPtr)
		newBuyerAddressHistory.save()