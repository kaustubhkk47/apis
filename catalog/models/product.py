from django.db import models

from users.models import Seller
from .category import Category
from django.template.defaultfilters import slugify
from decimal import Decimal
import datetime

#Make changes in model, validate, populate and serializer 
#Also make changes in upload script

class Product(models.Model):
    seller = models.ForeignKey(Seller)
    category = models.ForeignKey(Category)

    name = models.CharField(max_length=255, blank=False)

    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    unit = models.CharField(max_length=15, blank=False)
    tax = models.DecimalField(max_digits=5, decimal_places=2)
    min_price_per_unit = models.DecimalField(max_digits=7, decimal_places=2, default=0.0)

    lot_size = models.PositiveIntegerField(default=1)
    price_per_lot = models.DecimalField(max_digits=10, decimal_places=2, blank=False)

    image_path = models.TextField(blank=True)
    image_name = models.TextField(blank=True)
    image_numbers = models.TextField(blank=True)

    verification = models.BooleanField(default=False)
    show_online = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.CharField(max_length=100, blank=True)

    display_name = models.TextField()

    delete_status = models.BooleanField(default=False)
    is_catalog = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

class ProductDetails(models.Model):

    product = models.OneToOneField(Product)

    seller_catalog_number = models.CharField(max_length=200, blank=True)
    brand = models.CharField(max_length=100, blank=True)

    description = models.TextField()
    gender = models.CharField(max_length=20, blank=True)
    pattern = models.CharField(max_length=40, blank=True)
    style = models.CharField(max_length=40, blank=True)
    fabric_gsm = models.CharField(max_length=40, blank=True)
    sleeve = models.CharField(max_length=40, blank=True)
    neck_collar_type = models.CharField(max_length=40, blank=True)
    length = models.CharField(max_length=40, blank=True)
    work_decoration_type = models.CharField(max_length=40, blank=True)
    colours = models.CharField(max_length=100, blank=True)
    sizes = models.CharField(max_length=100, blank=True)
    #fabric = models.CharField(max_length=100, blank=True)
    special_feature = models.TextField(blank=True)
    packaging_details = models.TextField(blank=True)
    availability = models.TextField(blank=True)
    dispatched_in = models.TextField(blank=True)
    lot_description = models.TextField(blank=True)
    weight_per_unit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.0)

    sample_type = models.TextField(blank=True)
    sample_description = models.TextField(blank=True)
    sample_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.0)

    manufactured_country = models.CharField(max_length=50, blank=True, default="India")
    manufactured_city = models.CharField(max_length=50, blank=True)
    warranty = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    remarks = models.TextField()

    def __unicode__(self):
        return self.product.name

def validateProductData(product, oldproduct, is_new):

    flag = 0

    if not "name" in product or not product["name"]!=None:
        flag = 1
        product["name"] = oldproduct.name
    if not "price_per_unit" in product or not product["price_per_unit"]!=None:
        flag = 1
        product["price_per_unit"] = oldproduct.price_per_unit
    if not "unit" in product or not product["unit"]!=None:
        product["unit"] = oldproduct.unit
    if not "tax" in product or not product["tax"]!=None:
        product["tax"] = oldproduct.tax
    if not "min_price_per_unit" in product or not product["min_price_per_unit"]!=None:
        product["min_price_per_unit"] = oldproduct.min_price_per_unit
    if not "lot_size" in product or not product["lot_size"]!=None:
        flag = 1
        product["lot_size"] = oldproduct.lot_size
    if not "price_per_lot" in product or not product["price_per_lot"]!=None:
        flag = 1
        product["price_per_lot"] = oldproduct.price_per_lot
    if not "verification" in product or not product["verification"]!=None:
        product["verification"] = oldproduct.verification
    if not "show_online" in product or not product["show_online"]!=None:
        product["show_online"] = oldproduct.show_online
    if not "slug" in product or not product["slug"]!=None:
        product["slug"] = oldproduct.slug
    if not "display_name" in product or not product["display_name"]!=None:
        product["display_name"] = oldproduct.display_name
    if not "is_catalog" in product or not product["is_catalog"]!=None:
        product["is_catalog"] = oldproduct.is_catalog
    if not "delete_status" in product or not product["delete_status"]!=None:
        product["delete_status"] = oldproduct.delete_status
        
    if is_new == 1 and flag == 1:
        return False

    return True

def validateProductDetailsData(productdetails, oldproductdetails):
    if not "seller_catalog_number" in productdetails or not productdetails["seller_catalog_number"]!=None:
        productdetails["seller_catalog_number"] = oldproductdetails.seller_catalog_number
    if not "brand" in productdetails or not productdetails["brand"]!=None:
        productdetails["brand"] = oldproductdetails.brand
    if not "description" in productdetails or not productdetails["description"]!=None:
        productdetails["description"] = oldproductdetails.description
    if not "gender" in productdetails or not productdetails["gender"]!=None:
        productdetails["gender"] = oldproductdetails.gender
    if not "pattern" in productdetails or not productdetails["pattern"]!=None:
        productdetails["pattern"] = oldproductdetails.pattern
    if not "style" in productdetails or not productdetails["style"]!=None:
        productdetails["style"] = oldproductdetails.style
    if not "sleeve" in productdetails or not productdetails["sleeve"]!=None:
        productdetails["sleeve"] = oldproductdetails.sleeve
    if not "fabric_gsm" in productdetails or not productdetails["fabric_gsm"]!=None:
        productdetails["fabric_gsm"] = oldproductdetails.fabric_gsm
    if not "neck_collar_type" in productdetails or not productdetails["neck_collar_type"]!=None:
        productdetails["neck_collar_type"] = oldproductdetails.neck_collar_type
    if not "length" in productdetails or not productdetails["length"]!=None:
        productdetails["length"] = oldproductdetails.length
    if not "work_decoration_type" in productdetails or not productdetails["work_decoration_type"]!=None:
        productdetails["work_decoration_type"] = oldproductdetails.work_decoration_type
    if not "colours" in productdetails or not productdetails["colours"]!=None:
        productdetails["colours"] = oldproductdetails.colours
    if not "sizes" in productdetails or not productdetails["sizes"]!=None:
        productdetails["sizes"] = oldproductdetails.sizes
    if not "special_feature" in productdetails or not productdetails["special_feature"]!=None:
        productdetails["special_feature"] = oldproductdetails.special_feature
    if not "manufactured_country" in productdetails or not productdetails["manufactured_country"]!=None:
        productdetails["manufactured_country"] = oldproductdetails.manufactured_country
    if not "warranty" in productdetails or not productdetails["warranty"]!=None:
        productdetails["warranty"] = oldproductdetails.warranty
    if not "remarks" in productdetails or not productdetails["remarks"]!=None:
        productdetails["remarks"] = oldproductdetails.remarks
    if not "packaging_details" in productdetails or not productdetails["packaging_details"]!=None:
        productdetails["packaging_details"] = oldproductdetails.packaging_details
    if not "availability" in productdetails or not productdetails["availability"]!=None:
        productdetails["availability"] = oldproductdetails.availability
    if not "dispatched_in" in productdetails or not productdetails["dispatched_in"]!=None:
        productdetails["dispatched_in"] = oldproductdetails.dispatched_in
    if not "manufactured_city" in productdetails or not productdetails["manufactured_city"]!=None:
        productdetails["manufactured_city"] = oldproductdetails.manufactured_city
    if not "lot_description" in productdetails or not productdetails["lot_description"]!=None:
        productdetails["lot_description"] = oldproductdetails.lot_description
    if not "weight_per_unit" in productdetails or not productdetails["weight_per_unit"]!=None:
        productdetails["weight_per_unit"] = oldproductdetails.weight_per_unit
    if not "sample_type" in productdetails or not productdetails["sample_type"]!=None:
        productdetails["sample_type"] = oldproductdetails.sample_type
    if not "sample_description" in productdetails or not productdetails["sample_description"]!=None:
        productdetails["sample_description"] = oldproductdetails.sample_description
    if not "sample_price" in productdetails or not productdetails["sample_price"]!=None:
        productdetails["sample_price"] = oldproductdetails.sample_price

def populateProductData(productPtr, product):
    productPtr.name = product["name"]
    productPtr.price_per_unit = Decimal(product["price_per_unit"])
    productPtr.unit = product["unit"]
    productPtr.tax = Decimal(product["tax"])
    productPtr.min_price_per_unit = Decimal(product["min_price_per_unit"])
    productPtr.lot_size = int(product["lot_size"])
    productPtr.price_per_lot = Decimal(product["price_per_lot"])
    productPtr.verification = bool(product["verification"])
    productPtr.show_online = bool(product["show_online"])
    productPtr.slug = slugify(product["name"])
    productPtr.display_name = product["display_name"]
    productPtr.is_catalog = product["is_catalog"]
    productPtr.delete_status = product["delete_status"]
    if "image_count" in product and product["image_count"]!=None:
        nowtime = datetime.datetime.now()
        productPtr.image_path = "media/productimages/" + str(productPtr.seller.id) + "/" + nowtime.strftime('%Y%m%d%H%M%S') + "/"
        productPtr.image_name = slugify(productPtr.display_name)
        image_numbers = {}
        for i in range(1, product["image_count"] + 1):
            image_numbers[i] = i
        productPtr.image_numbers = str(image_numbers)

def populateProductDetailsData(productDetailsPtr, productdetails):
    productDetailsPtr.seller_catalog_number = productdetails["seller_catalog_number"]
    productDetailsPtr.brand = productdetails["brand"]
    productDetailsPtr.description = productdetails["description"]
    productDetailsPtr.gender = productdetails["gender"]
    productDetailsPtr.pattern = productdetails["pattern"]
    productDetailsPtr.style = productdetails["style"]
    productDetailsPtr.fabric_gsm = productdetails["fabric_gsm"]
    productDetailsPtr.sleeve = productdetails["sleeve"]
    productDetailsPtr.neck_collar_type = productdetails["neck_collar_type"]
    productDetailsPtr.length = productdetails["length"]
    productDetailsPtr.work_decoration_type = productdetails["work_decoration_type"]
    productDetailsPtr.colours = productdetails["colours"]
    productDetailsPtr.sizes = productdetails["sizes"]
    productDetailsPtr.special_feature = productdetails["special_feature"]
    productDetailsPtr.manufactured_country = productdetails["manufactured_country"]
    productDetailsPtr.warranty = productdetails["warranty"]
    productDetailsPtr.remarks = productdetails["remarks"]
    productDetailsPtr.packaging_details = productdetails["packaging_details"]
    productDetailsPtr.availability = productdetails["availability"]
    productDetailsPtr.dispatched_in = productdetails["dispatched_in"]
    productDetailsPtr.manufactured_city = productdetails["manufactured_city"]
    productDetailsPtr.lot_description = productdetails["lot_description"]
    productDetailsPtr.weight_per_unit = Decimal(productdetails["weight_per_unit"])
    productDetailsPtr.sample_type = productdetails["sample_type"]
    productDetailsPtr.sample_description = productdetails["sample_description"]
    productDetailsPtr.sample_price = Decimal(productdetails["sample_price"])