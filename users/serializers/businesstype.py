
def parse_business_type(business_types_queryset, parameters = {}):

	business_types = []

	for business_type in business_types_queryset:
		business_type_entry = serialize_business_type(business_type, parameters)
		business_types.append(business_type_entry)

	return business_types

def serialize_business_type(business_type_entry, parameters = {}):

	business_type = {}

	business_type["businesstypeID"] = business_type_entry.id
	business_type["business_type"] = business_type_entry.business_type
	business_type["description"] = business_type_entry.description

	return business_type