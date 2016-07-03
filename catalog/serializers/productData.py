def parseProductColourType(ProductColourTypeQuerySet, parameters = {}):

	ProductColourTypes = []

	for ProductColourType in ProductColourTypeQuerySet:
		ProductColourTypeEntry = serializeProductColourType(ProductColourType, parameters)
		ProductColourTypes.append(ProductColourTypeEntry)

	return ProductColourTypes

def serializeProductColourType(productColourTypeEntry, parameters={}):
	productColourType = {}

	productColourType["fabric_type"] = productColourTypeEntry.fabric_type
	productColourType["created_at"] = productColourTypeEntry.created_at
	productColourType["updated_at"] = productColourTypeEntry.updated_at

	return productColourType

def parseProductFabricType(ProductFabricTypeQuerySet, parameters = {}):

	ProductFabricTypes = []

	for ProductFabricType in ProductFabricTypeQuerySet:
		ProductFabricTypeEntry = serializeProductFabricType(ProductFabricType, parameters)
		ProductFabricTypes.append(ProductFabricTypeEntry)

	return ProductFabricTypes

def serializeProductFabricType(productFabricTypeEntry, parameters={}):
	productFabricType = {}

	productFabricType["fabric_type"] = productFabricTypeEntry.fabric_type
	productFabricType["created_at"] = productFabricTypeEntry.created_at
	productFabricType["updated_at"] = productFabricTypeEntry.updated_at

	return productFabricType