from django.db import models

from users.models import Seller
from .category import Category
from django.template.defaultfilters import slugify
from decimal import Decimal

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

    images = models.CommaSeparatedIntegerField(max_length=255, blank=True)

    verification = models.BooleanField(default=False)
    show_online = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.CharField(max_length=100, blank=True)

    delete_status = models.BooleanField(default=False)

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
    gsm = models.CharField(max_length=40, blank=True)
    sleeve = models.CharField(max_length=40, blank=True)
    neck_collar_type = models.CharField(max_length=40, blank=True)
    length = models.CharField(max_length=40, blank=True)
    work_decoration_type = models.CharField(max_length=40, blank=True)
    colours = models.CharField(max_length=100, blank=True)
    sizes = models.CharField(max_length=100, blank=True)
    fabric = models.CharField(max_length=100, blank=True)
    special_feature = models.TextField(blank=True)

    manufactured_country = models.CharField(max_length=50, blank=True, default="India")
    warranty = models.CharField(max_length=100, blank=True)

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

    print product["show_online"]
        
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
    if not "gsm" in productdetails or not productdetails["gsm"]!=None:
        productdetails["gsm"] = oldproductdetails.gsm
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
    if not "fabric" in productdetails or not productdetails["fabric"]!=None:
        productdetails["fabric"] = oldproductdetails.fabric
    if not "remarks" in productdetails or not productdetails["remarks"]!=None:
        productdetails["remarks"] = oldproductdetails.remarks

def populateProductData(productPtr, product):
    productPtr.name = product["name"]
    productPtr.price_per_unit = Decimal(product["price_per_unit"])
    productPtr.unit = product["unit"]
    productPtr.tax = Decimal(product["tax"])
    productPtr.lot_size = int(product["lot_size"])
    productPtr.price_per_lot = Decimal(product["price_per_lot"])
    productPtr.verification = bool(product["verification"])
    productPtr.show_online = bool(product["show_online"])
    productPtr.slug = slugify(product["name"])
    productPtr.min_price_per_unit = Decimal(product["min_price_per_unit"])

def populateProductDetailsData(productDetailsPtr, productdetails):
    productDetailsPtr.seller_catalog_number = productdetails["seller_catalog_number"]
    productDetailsPtr.brand = productdetails["brand"]
    productDetailsPtr.description = productdetails["description"]
    productDetailsPtr.gender = productdetails["gender"]
    productDetailsPtr.pattern = productdetails["pattern"]
    productDetailsPtr.style = productdetails["style"]
    productDetailsPtr.gsm = productdetails["gsm"]
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
    productDetailsPtr.fabric = productdetails["fabric"]