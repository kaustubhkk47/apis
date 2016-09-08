from ..models.internalUser import *

def serialize_internaluser(internaluser_entry, parameters = {}):
	internaluser = {
		"internaluserID":internaluser_entry.id,
		"name":internaluser_entry.name,
		"email":internaluser_entry.email,
		"mobile_number":internaluser_entry.mobile_number,
		"created_at":internaluser_entry.created_at,
		"updated_at":internaluser_entry.updated_at
	}
	return internaluser

def parseInternalUser(internal_users_queryset, parameters = {}):

    internal_users = []

    for internal_user in internal_users_queryset:
        internal_user_entry = serialize_internaluser(internal_user, parameters)
        internal_users.append(internal_user_entry)

    return internal_users