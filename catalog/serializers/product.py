from decimal import Decimal
import settings

from ..models.productLot import ProductLot

def serialize_product_lots(productsItem):

    productLotsQuerySet = ProductLot.objects.filter(product__id = productsItem.id)
    productLots = []

    for productLot in productLotsQuerySet:
        productLotEntry = {
            "productlotID" : productLot.id,
            "lot_size_from":productLot.lot_size_from,
            "lot_size_to":productLot.lot_size_to,
            "price_per_unit":productLot.price_per_unit
        }
        productLots.append(productLotEntry)

    return productLots

def serialize_product(productsItem):

    product = {}

    product["productID"] = productsItem.id
    product["name"] = productsItem.name
    product["price_per_unit"] = productsItem.price_per_unit
    product["tax"] = productsItem.tax
    product["lot_size"] = productsItem.lot_size
    product["price_per_lot"] = productsItem.price_per_lot
    product["verification"] = productsItem.verification
    product["show_online"] = productsItem.show_online
    product["created_at"] = productsItem.created_at
    product["updated_at"] = productsItem.updated_at
    product["slug"] = productsItem.slug
    product["min_price_per_unit"] = productsItem.min_price_per_unit
    discounted_price = Decimal(productsItem.price_per_unit)*(1- Decimal(productsItem.min_price_per_unit)/100)
    product["discounted_price_per_unit"] = '%.2f' % discounted_price

    product["seller"] = {
        "seller_name" : productsItem.seller.name,
        "sellerID" : productsItem.seller.id
    }

    product["category"] = {
        "category_name" : productsItem.category.name,
        "categoryID" : productsItem.category.id,
        "category_slug" : productsItem.category.slug
    }

    product["product_lot"] = serialize_product_lots(productsItem)
    product["url"] = productsItem.category.slug + "-" + str(productsItem.category.id) + "/" + productsItem.slug+ "-" + str(productsItem.id)


    return product

def serialize_product_details(productsItem, product):

    details ={}

    details["detailsID"] = productsItem.productdetails.id
    details["seller_catalog_number"] = productsItem.productdetails.seller_catalog_number
    details["lot_description"] = productsItem.productdetails.description
    details["brand"] = productsItem.productdetails.brand
    details["pattern"] = productsItem.productdetails.pattern
    details["style"] = productsItem.productdetails.style
    details["gsm"] = productsItem.productdetails.gsm
    details["gender"] = productsItem.productdetails.gender
    details["fabric"] = productsItem.productdetails.fabric
    details["sleeve"] = productsItem.productdetails.sleeve
    details["neck_collar_type"] = productsItem.productdetails.neck_collar_type
    details["length"] = productsItem.productdetails.length
    details["work_decoration_type"] = productsItem.productdetails.work_decoration_type
    details["colours"] = productsItem.productdetails.colours
    details["sizes"] = productsItem.productdetails.sizes
    details["special_feature"] = productsItem.productdetails.special_feature

    details["manufactured_country"] = productsItem.productdetails.manufactured_country
    details["warranty"] = productsItem.productdetails.warranty
    details["remarks"] = productsItem.productdetails.remarks

    product["details"] = details

    return product

def multiple_products_parser(productQuerySet):
    products = []
    for productsItem in productQuerySet:
        product = serialize_product(productsItem)

        if hasattr(productsItem, 'productdetails'):
            product = serialize_product_details(productsItem, product)

        products.append(product)
    return products
