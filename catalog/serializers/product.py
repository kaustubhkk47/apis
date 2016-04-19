from decimal import Decimal
import settings

def category_products_parser(productQuerySet):
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
            product["price_per_unit"] = productsItem.product.price_per_unit
            product["tax"] = productsItem.product.tax
            product["lot_size"] = productsItem.product.lot_size
            product["price_per_lot"] = productsItem.product.price_per_lot
            product["verification"] = productsItem.product.verification
            product["show_online"] = productsItem.product.show_online
            product["slug"] = productsItem.product.slug
            product["max_discount"] = productsItem.product.max_discount
            discounted_price = Decimal(productsItem.product.price_per_unit)*(1-
                productsItem.product.max_discount/100)
            product["discounted_price_per_unit"] = '%.2f' % discounted_price

            product["seller_name"] = productsItem.product.seller.name
            product["seller_id"] = productsItem.product.seller.id

            product["category_name"] = productsItem.product.category.name
            product["category_id"] = productsItem.product.category.id
            product["category_slug"] = productsItem.product.category.slug


            product["product_lot"] = [{
                "lot_size_from":productsItem.lot_size_from,
                "lot_size_to":productsItem.lot_size_to,
                "lot_discount":productsItem.lot_discount,
                "lot_id":productsItem.id
            }]
            
            product["url"] = settings.BASE_WEBAPP_URL + productsItem.product.category.slug + "-" + str(productsItem.product.category.id) + "/" + productsItem.product.slug+ "-" + str(productsItem.product.id)
            

            products.append(product)
            products_hash[productsItem.product.id] = len(products_hash)

    return products


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
            product["price_per_unit"] = productsItem.product.price_per_unit
            product["tax"] = productsItem.product.tax
            product["lot_size"] = productsItem.product.lot_size
            product["price_per_lot"] = productsItem.product.price_per_lot
            product["verification"] = productsItem.product.verification
            product["show_online"] = productsItem.product.show_online
            product["created_at"] = productsItem.product.created_at
            product["updated_at"] = productsItem.product.updated_at
            product["slug"] = productsItem.product.slug
            product["max_discount"] = productsItem.product.max_discount
            discounted_price = Decimal(productsItem.product.price_per_unit)*(1-
                productsItem.product.max_discount/100)
            product["discounted_price_per_unit"] = '%.2f' % discounted_price

            product["seller_catalog_number"] = productsItem.product.productdetails.seller_catalog_number
            product["description"] = productsItem.product.productdetails.description
            product["brand"] = productsItem.product.productdetails.brand
            product["pattern"] = productsItem.product.productdetails.pattern
            product["style"] = productsItem.product.productdetails.style
            product["gsm"] = productsItem.product.productdetails.gsm
            product["sleeve"] = productsItem.product.productdetails.sleeve
            product["neck_collar_type"] = productsItem.product.productdetails.neck_collar_type
            product["length"] = productsItem.product.productdetails.length
            product["work_decoration_type"] = productsItem.product.productdetails.work_decoration_type
            product["colours"] = productsItem.product.productdetails.colours
            product["sizes"] = productsItem.product.productdetails.sizes
            product["special_feature"] = productsItem.product.productdetails.special_feature

            product["manufactured_country"] = productsItem.product.productdetails.manufactured_country
            product["warranty"] = productsItem.product.productdetails.warranty
            product["remarks"] = productsItem.product.productdetails.remarks

            product["seller_name"] = productsItem.product.seller.name
            product["seller_id"] = productsItem.product.seller.id

            product["category_name"] = productsItem.product.category.name
            product["category_id"] = productsItem.product.category.id
            product["category_slug"] = productsItem.product.category.slug

            product["product_lot"] = [{
                "lot_size_from":productsItem.lot_size_from,
                "lot_size_to":productsItem.lot_size_to,
                "lot_discount":productsItem.lot_discount,
                "lot_id":productsItem.id
            }]

            products.append(product)
            products_hash[productsItem.product.id] = len(products_hash)

    return products
