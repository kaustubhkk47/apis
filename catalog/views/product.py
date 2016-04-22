from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string

from ..models.category import Category
from ..models.product import Product, validateProductData, ProductDetails, validateProductDetailsData
from ..models.productLot import ProductLot, validateProductLotData, parseMaxDiscount
from ..serializers.product import multiple_products_parser, serialize_product
from users.models.seller import Seller
import json
from django.template.defaultfilters import slugify
from decimal import Decimal


def get_product_details(request, productsArr=[]):

    try:
        if len(productsArr) == 0:
            products = Product.objects.filter(delete_status=False, seller__delete_status=False, category__delete_status=False).select_related(
                'seller', 'productdetails', 'category')
            closeDBConnection()
        else:
            products = Product.objects.filter(id__in=productsArr, delete_status=False, seller__delete_status=False,
                category__delete_status=False).select_related('seller', 'productdetails', 'category')
            closeDBConnection()

        response = multiple_products_parser(products)
        statusCode = "2XX"
        body = {"products": response}
    except Exception as e:
        statusCode = "4XX"
        body = {"error": "Invalid product"}

    return customResponse(statusCode, body)


def post_new_product(request):
    try:
        requestbody = request.body.decode("utf-8")
        product = convert_keys_to_string(json.loads(requestbody))
    except Exception as e:
        print e
        return customResponse("4XX", {"error": "Invalid data sent in request"})

    if not len(product) or not validateProductData(product, Product(), 1):
        return customResponse("4XX", {"error": "Invalid data for product sent"})

    if not "sellerID" in product or not product["sellerID"]:
        return customResponse("4XX", {"error": "Seller id for product not sent"})

    sellerPtr = Seller.objects.filter(id=int(product["sellerID"]))
    if len(sellerPtr) == 0:
        return customResponse("4XX", {"error": "Invalid id for seller sent"})
    sellerPtr = sellerPtr[0]

    if not "categoryID" in product or not product["categoryID"]:
        return customResponse("4XX", {"error": "Category id for product not sent"})

    categoryPtr = Category.objects.filter(id=int(product["categoryID"]))
    if len(categoryPtr) == 0:
        return customResponse("4XX", {"error": "Invalid id for category sent"})
    categoryPtr = categoryPtr[0]

    if not "product_lot" in product or not product["product_lot"] or not validateProductLotData(product["product_lot"]):
        return customResponse("4XX", {"error": "Product lots for product not properly sent"})

    if not "details" in product or not product["details"]:
        product["details"] = {}

    validateProductDetailsData(product["details"], ProductDetails())

    product["slug"] = slugify(product["name"])
    product["max_discount"] = parseMaxDiscount(product["product_lot"])

    try:

        newProduct = Product(category=categoryPtr,seller=sellerPtr,name=product["name"], price_per_unit=Decimal(product["price_per_unit"]), unit=product["unit"],
            tax=Decimal(product["tax"]),max_discount=Decimal(product["max_discount"]),lot_size=int(product["lot_size"]),price_per_lot=Decimal(product["price_per_lot"]),
            verification=bool(product["verification"]),show_online=bool(product["show_online"]),slug=product["slug"])
        newProduct.save()

        productLots = product["product_lot"]
        for productLot in productLots:
            newProductLot = ProductLot(product=newProduct,lot_size_from=productLot["lot_size_from"],
                lot_size_to=productLot["lot_size_to"],lot_discount=productLot["lot_discount"])
            newProductLot.save()

        productdetails = product["details"]
        newProductDetails = ProductDetails(product=newProduct, seller_catalog_number=productdetails["seller_catalog_number"],
            brand=productdetails["brand"], description=productdetails["description"],
            gender=productdetails["gender"], pattern=productdetails["pattern"],
            style=productdetails["style"], gsm=productdetails["gsm"],
            sleeve=productdetails["sleeve"], neck_collar_type=productdetails["neck_collar_type"],
            length=productdetails["length"], work_decoration_type=productdetails["work_decoration_type"],
            colours=productdetails["colours"], sizes=productdetails["sizes"],
            special_feature=productdetails["special_feature"], manufactured_country=productdetails["manufactured_country"],
            warranty=productdetails["warranty"], remarks=productdetails["remarks"])

        newProductDetails.save()

    except Exception as e:
        print e
        closeDBConnection()
        return customResponse("4XX", {"error": "unable to create entry in db"})
    else:
        closeDBConnection()
        return customResponse("2XX", {"product": serialize_product(newProduct)})