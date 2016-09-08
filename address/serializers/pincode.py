from .city import serialize_city

def parse_pincode(pincodeQuerySet):
	pincodes = []
	for pincodesItem in pincodeQuerySet:
		pincode = serialize_pincode(pincodesItem)
		pincodes.append(pincode)
	return pincodes

def serialize_pincode(pincodeItem):

	pincode = {}

	pincode["pincodeID"] = pincodeItem.id
	pincode["pincode"] = pincodeItem.pincode

	pincode["city"] = serialize_city(pincodeItem.city)

	return pincode