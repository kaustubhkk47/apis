
def multiple_products_parser(productQuerySet):
    products = []
    products_hash = {}

    for i in range(len(productQuerySet)):
        productsItem = productQuerySet[i]
        
        if productsItem.product.id in products_hash:
            productLot = {
                "lot_size_from":productsItem.lot_size_from,
                "lot_size_to":productsItem.lot_size_to,
                "lot_discount":productsItem.lot_discount,
                "lot_id":productsItem.id
            }

            products[products_hash[productsItem.product.id]]["product_lot"].append(productLot)
        else :
            product = {}
            product["product_id"] = productsItem.product.id
            product["name"] = productsItem.product.name
            product["seller_name"] = productsItem.product.seller.name
            product["seller_id"] = productsItem.product.seller.id
            product["category_name"] = productsItem.product.category.name
            product["category_id"] = productsItem.product.category.id
            product["price_per_unit"] = productsItem.product.price_per_unit
            product["tax"] = productsItem.product.tax
            product["lot_size"] = productsItem.product.lot_size
            product["price_per_lot"] = productsItem.product.price_per_lot
            product["seller_catalog_number"] = productsItem.product.seller_catalog_number
            product["brand"] = productsItem.product.brand
            product["slug"] = productsItem.product.slug
            product["manufactured_country"] = productsItem.product.manufactured_country
            product["warranty"] = productsItem.product.warranty
            product["remarks"] = productsItem.product.remarks
            product["verification"] = productsItem.product.verification
            product["show_online"] = productsItem.product.show_online
            product["created_at"] = productsItem.product.created_at
            product["updated_at"] = productsItem.product.updated_at

            product["product_lot"] = [{
                "lot_size_from":productsItem.lot_size_from,
                "lot_size_to":productsItem.lot_size_to,
                "lot_discount":productsItem.lot_discount,
                "lot_id":productsItem.id
            }]

            products.append(product)
            products_hash[productsItem.product.id] = len(products_hash)

    return products