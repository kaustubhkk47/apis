import settings

def serialize_categories(categoriesItem, parameters = {}):
    category = {}
    category["name"]= categoriesItem.name
    category["display_name"]= categoriesItem.display_name
    category["slug"]= categoriesItem.slug
    category["created_at"]= categoriesItem.created_at
    category["updated_at"]= categoriesItem.updated_at
    category["categoryID"]= categoriesItem.id
    category["id"]= categoriesItem.id
    category["url"]= categoriesItem.slug + "-" + str(categoriesItem.id)
    
    return category


def categories_parser(categoryQuerySet, parameters={}):
    categories = []

    for i in range(len(categoryQuerySet)):
        categories.append(serialize_categories(categoryQuerySet[i], parameters))

    return categories
