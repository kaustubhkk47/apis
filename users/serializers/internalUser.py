from ..models.internalUser import *

def serialize_internaluser(internaluser_entry):
	internaluser = {
		"name":internaluser_entry.name,
		"email":internaluser_entry.email,
		"mobile_number":internaluser_entry.mobile_number,
		"password":internaluser_entry.password,
		"created_at":internaluser_entry.created_at,
		"updated_at":internaluser_entry.updated_at
	}
	return internaluser