from address.serializers.pincode import serialize_pincode

def parseServiceablePincodes(serviceablePincodeQuerySet, parameters = {}):

	serviceablePincodes = []

	for serviceablePincode in serviceablePincodeQuerySet:
		serviceablePincodeEntry = serializeServiceablePincodes(serviceablePincode, parameters)
		serviceablePincodes.append(serviceablePincodeEntry)

	return serviceablePincodes

def serializeServiceablePincodes(serviceablePincodeEntry, parameters = {}):
	serviceablePincode = {}
	serviceablePincode["logisticspartnerID"] = serviceablePincodeEntry.logistics_partner_id
	serviceablePincode["pincodeID"] = serviceablePincodeEntry.pincode_id
	serviceablePincode["delivery_available"] = serviceablePincodeEntry.delivery_available
	serviceablePincode["pickup_available"] = serviceablePincodeEntry.pickup_available
	serviceablePincode["regular_delivery_available"] = serviceablePincodeEntry.regular_delivery_available
	serviceablePincode["regular_pickup_available"] = serviceablePincodeEntry.regular_pickup_available
	serviceablePincode["cod_available"] = serviceablePincodeEntry.cod_available

	serviceablePincode["pincode"] = serialize_pincode(serviceablePincodeEntry.pincode)
	
	return serviceablePincode