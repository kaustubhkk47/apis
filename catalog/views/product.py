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
            newProductLot = ProductLot(product=newProduct,lot_size_from=int(productLot["lot_size_from"]),
                lot_size_to=int(productLot["lot_size_to"]),lot_discount=Decimal(productLot["lot_discount"]))
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
        closeDBConnection()
        return customResponse("4XX", {"error": "unable to create entry in db"})
    else:
        closeDBConnection()
        return customResponse("2XX", {"product": serialize_product(newProduct)})

def update_product(request):
    try:
        requestbody = request.body.decode("utf-8")
        product = convert_keys_to_string(json.loads(requestbody))
    except Exception as e:
        return customResponse("4XX", {"error": "Invalid data sent in request"})

    if not len(product) or not "productID" in product or not product["productID"]:
        return customResponse("4XX", {"error": "Id for product not sent"})

    productPtr = Product.objects.filter(id=int(product["productID"])).select_related('productdetails')

    if len(productPtr) == 0:
        return customResponse("4XX", {"error": "Invalid id for product sent"})

    productPtr = productPtr[0]

    detailsPresent = 1
    detailsSent = 0
    productlotSent = 0

    if not validateProductData(product, productPtr, 0):
        return customResponse("4XX", {"error": "Invalid data for product sent"})

    try:
        productPtr.name = product["name"]
        productPtr.price_per_unit = Decimal(product["price_per_unit"])
        productPtr.unit = product["unit"]
        productPtr.tax = Decimal(product["tax"])
        productPtr.lot_size = int(product["lot_size"])
        productPtr.price_per_lot = Decimal(product["price_per_lot"])
        productPtr.verification = bool(product["verification"])
        productPtr.show_online = bool(product["show_online"])
        productPtr.slug = slugify(product["name"])

        if "details" in product and product["details"]:
            detailsSent = 1
            productdetails = product["details"]
            if hasattr(productPtr, "productdetails"):
                validateProductDetailsData(productdetails, productPtr.productdetails)
                productPtr.productdetails.seller_catalog_number = productdetails["seller_catalog_number"]
                productPtr.productdetails.brand = productdetails["brand"]
                productPtr.productdetails.description = productdetails["description"]
                productPtr.productdetails.gender = productdetails["gender"]
                productPtr.productdetails.pattern = productdetails["pattern"]
                productPtr.productdetails.style = productdetails["style"]
                productPtr.productdetails.gsm = productdetails["gsm"]
                productPtr.productdetails.sleeve = productdetails["sleeve"]
                productPtr.productdetails.neck_collar_type = productdetails["neck_collar_type"]
                productPtr.productdetails.length = productdetails["length"]
                productPtr.productdetails.work_decoration_type = productdetails["work_decoration_type"]
                productPtr.productdetails.colours = productdetails["colours"]
                productPtr.productdetails.sizes = productdetails["sizes"]
                productPtr.productdetails.special_feature = productdetails["special_feature"]
                productPtr.productdetails.manufactured_country = productdetails["manufactured_country"]
                productPtr.productdetails.warranty = productdetails["warranty"]
                productPtr.productdetails.remarks = productdetails["remarks"]

            else:
                detailsPresent = 0
                validateProductDetailsData(productdetails, ProductDetails())
                newProductDetails = ProductDetails(product=productPtr, seller_catalog_number=productdetails["seller_catalog_number"],
                    brand=productdetails["brand"], description=productdetails["description"],
                    gender=productdetails["gender"], pattern=productdetails["pattern"],
                    style=productdetails["style"], gsm=productdetails["gsm"],
                    sleeve=productdetails["sleeve"], neck_collar_type=productdetails["neck_collar_type"],
                    length=productdetails["length"], work_decoration_type=productdetails["work_decoration_type"],
                    colours=productdetails["colours"], sizes=productdetails["sizes"],
                    special_feature=productdetails["special_feature"], manufactured_country=productdetails["manufactured_country"],
                    warranty=productdetails["warranty"], remarks=productdetails["remarks"])
        if "product_lot" in product and product["product_lot"]:
            productlotSent = 1
            if not validateProductLotData(product["product_lot"]):
                return customResponse("4XX", {"error": "Product lots for product not properly sent"})

            productLots = product["product_lot"]

            ProductLot.objects.filter(product_id=int(product["productID"])).delete()
            productPtr.max_discount = Decimal(parseMaxDiscount(productLots))

            for productLot in productLots:
                newProductLot = ProductLot(product=productPtr,lot_size_from=int(productLot["lot_size_from"]),
                lot_size_to=int(productLot["lot_size_to"]),lot_discount=Decimal(productLot["lot_discount"]))
                newProductLot.save()
                
        productPtr.save()
        if detailsSent == 1 and detailsPresent == 1:
            productPtr.productdetails.save()
        if detailsPresent == 0:
            newProductDetails.save()
        

    except Exception as e:
        print e
        closeDBConnection()
        return customResponse("4XX", {"error": "could not update"})
    else:
        closeDBConnection()
        return customResponse("2XX", {"product": serialize_product(productPtr)})