from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string

from ..models.category import Category
from ..models.product import Product, validateProductData, ProductDetails, validateProductDetailsData, populateProductData, populateProductDetailsData, filterProducts
from ..models.productLot import ProductLot, validateProductLotData, parseMinPricePerUnit, populateProductLotData
from ..serializers.product import multiple_products_parser, serialize_product
from users.models.seller import Seller
import json
from django.template.defaultfilters import slugify
from decimal import Decimal
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import logging
log = logging.getLogger("django")

def get_product_details(request, productParameters):
    try:
        products = filterProducts(productParameters)

        if "pageNumber" in productParameters:
            paginator = Paginator(products, productParameters["productsperPage"])
            try:
                pageProducts = paginator.page(productParameters["pageNumber"])
            except PageNotAnInteger:
                pageProducts = []
            except EmptyPage:
                pageProducts = []
            response = multiple_products_parser(pageProducts)
            body = {"products": response,"total_products":paginator.count, "total_pages":paginator.num_pages, "page_number":productParameters["pageNumber"]}
        else:
            response = multiple_products_parser(products)
            body = {"products": response}
            
        statusCode = "2XX"
    except Exception as e:
        log.critical(e)
        statusCode = "4XX"
        body = {"error": "Invalid product"}

    closeDBConnection()
    return customResponse(statusCode, body)


def post_new_product(request):
    try:
        requestbody = request.body.decode("utf-8")
        product = convert_keys_to_string(json.loads(requestbody))
    except Exception as e:
        return customResponse("4XX", {"error": "Invalid data sent in request"})

    if not len(product) or not validateProductData(product, Product(), 1):
        return customResponse("4XX", {"error": "Invalid data for product sent"})

    if not "sellerID" in product or product["sellerID"]==None:
        return customResponse("4XX", {"error": "Seller id for product not sent"})

    sellerPtr = Seller.objects.filter(id=int(product["sellerID"]))
    if len(sellerPtr) == 0:
        return customResponse("4XX", {"error": "Invalid id for seller sent"})
    sellerPtr = sellerPtr[0]

    if not "categoryID" in product or product["categoryID"]==None:
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
    product["min_price_per_unit"] = parseMinPricePerUnit(product["product_lot"])
    product["display_name"] = product["details"]["brand"] + " " +product["name"] + " " + product["details"]["seller_catalog_number"]

    try:

        newProduct = Product(category=categoryPtr,seller=sellerPtr)
        populateProductData(newProduct, product)
        newProduct.save()

        productLots = product["product_lot"]
        for productLot in productLots:
            newProductLot = ProductLot(product=newProduct)
            populateProductLotData(newProductLot, productLot)
            newProductLot.save()

        productdetails = product["details"]
        newProductDetails = ProductDetails(product=newProduct)
        populateProductDetailsData(newProductDetails, productdetails)

        newProductDetails.save()

    except Exception as e:
        log.critical(e)
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

    if not len(product) or not "productID" in product or product["productID"]==None:
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

    product["slug"] = slugify(product["name"])

    try:
        populateProductData(productPtr, product)
        
        if "details" in product and product["details"]:
            detailsSent = 1
            productdetails = product["details"]
            productPtr.display_name = product["details"]["brand"] + " " +product["name"] + " " + product["details"]["seller_catalog_number"]
            if hasattr(productPtr, "productdetails"):
                validateProductDetailsData(productdetails, productPtr.productdetails)
                populateProductDetailsData(productPtr.productdetails, productdetails)
            else:
                detailsPresent = 0
                validateProductDetailsData(productdetails, ProductDetails())
                newProductDetails = ProductDetails(product=productPtr)
                populateProductDetailsData(newProductDetails, productdetails)

        if "product_lot" in product and product["product_lot"]:
            productlotSent = 1
            if not validateProductLotData(product["product_lot"]):
                return customResponse("4XX", {"error": "Product lots for product not properly sent"})

            productLots = product["product_lot"]

            ProductLot.objects.filter(product_id=int(product["productID"])).delete()
            productPtr.min_price_per_unit = Decimal(parseMinPricePerUnit(productLots))    

            for productLot in productLots:
                newProductLot = ProductLot(product=productPtr)
                populateProductLotData(newProductLot, productLot)
                newProductLot.save()
                
        productPtr.save()
        if detailsSent == 1 and detailsPresent == 1:
            productPtr.productdetails.save()
        if detailsPresent == 0:
            newProductDetails.save()
        

    except Exception as e:
        log.critical(e)
        closeDBConnection()
        return customResponse("4XX", {"error": "could not update"})
    else:
        closeDBConnection()
        return customResponse("2XX", {"product": serialize_product(productPtr)})

def delete_product(request):
    try:
        requestbody = request.body.decode("utf-8")
        product = convert_keys_to_string(json.loads(requestbody))
    except Exception as e:
        return customResponse("4XX", {"error": "Invalid data sent in request"})

    if not len(product) or not "productID" in product or product["productID"]==None:
        return customResponse("4XX", {"error": "Id for product not sent"})

    productPtr = Product.objects.filter(id=int(product["productID"]))

    if len(productPtr) == 0:
        return customResponse("4XX", {"error": "Invalid id for product sent"})

    productPtr = productPtr[0]

    try:
        productPtr.delete_status = True
        productPtr.save()
    except Exception as e:
        log.critical(e)
        closeDBConnection()
        return customResponse("4XX", {"error": "could not delete"})
    else:
        closeDBConnection()
        return customResponse("2XX", {"product": "product deleted"})