from .state import serialize_state

def parse_city(cityQuerySet):
	citys = []
	for citysItem in cityQuerySet:
		city = serialize_city(citysItem)
		citys.append(city)
	return citys

def serialize_city(cityItem):

	city = {}

	city["cityID"] = cityItem.id
	city["name"] = cityItem.name

	city["state"] = serialize_state(cityItem.state)

	return city