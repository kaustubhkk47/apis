from decimal import Decimal
import settings

from ..models.productLot import ProductLot

def serialize_product_lots(productsItem):

    productLotsQuerySet = ProductLot.objects.filter(product__id = productsItem.id)
    productLots = []

    for productLot in productLotsQuerySet:
        productLotEntry = {
            "lot_size_from":productLot.lot_size_from,
            "lot_size_to":productLot.lot_size_to,
            "lot_discount":productLot.lot_discount,
            "lot_id":productLot.id
        }
        productLots.append(productLotEntry)

    return productLots

def serialize_product(productsItem):

    product = {}

    product["product_id"] = productsItem.id
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
    product["max_discount"] = productsItem.max_discount
    discounted_price = Decimal(productsItem.price_per_unit)*(1-
        productsItem.max_discount/100)
    product["discounted_price_per_unit"] = '%.2f' % discounted_price

    product["seller_name"] = productsItem.seller.name
    product["seller_id"] = productsItem.seller.id

    product["category_name"] = productsItem.category.name
    product["category_id"] = productsItem.category.id
    product["category_slug"] = productsItem.category.slug

    product["product_lot"] = serialize_product_lots(productsItem)

    return product

def serialize_product_details(productsItem, product):

    product["seller_catalog_number"] = productsItem.productdetails.seller_catalog_number
    product["description"] = productsItem.productdetails.description
    product["brand"] = productsItem.productdetails.brand
    product["pattern"] = productsItem.productdetails.pattern
    product["style"] = productsItem.productdetails.style
    product["gsm"] = productsItem.productdetails.gsm
    product["sleeve"] = productsItem.productdetails.sleeve
    product["neck_collar_type"] = productsItem.productdetails.neck_collar_type
    product["length"] = productsItem.productdetails.length
    product["work_decoration_type"] = productsItem.productdetails.work_decoration_type
    product["colours"] = productsItem.productdetails.colours
    product["sizes"] = productsItem.productdetails.sizes
    product["special_feature"] = productsItem.productdetails.special_feature

    product["manufactured_country"] = productsItem.productdetails.manufactured_country
    product["warranty"] = productsItem.productdetails.warranty
    product["remarks"] = productsItem.productdetails.remarks

    return product

def category_products_parser(productQuerySet):
    products = []
    products_hash = {}

    for productsItem in productQuerySet:
        product = serialize_product(productsItem)
        product["url"] = productsItem.category.slug + "-" + str(productsItem.category.id) + "/" + productsItem.slug+ "-" + str(productsItem.id)
        products.append(product)

    return products

def multiple_products_parser(productQuerySet):
    products = []
    for productsItem in productQuerySet:
        product = serialize_product(productsItem)
        product = serialize_product_details(productsItem, product)
        products.append(product)
    return products
