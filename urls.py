"""apis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.conf.urls import url, include
	2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from urlHandlers import catalog_handler, user_handler, order_handler, lead_handler, address_handler, blog_handler
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
	url(r'^admin/', admin.site.urls),
]

urlpatterns += [
	url(r'^category/$', catalog_handler.categories_details),
	url(r'^products/$', catalog_handler.product_details),
	url(r'^products/colour_type/$', catalog_handler.product_colour_details),
	url(r'^products/fabric_type/$', catalog_handler.product_fabric_details),
	url(r'^products/generatefile/$', catalog_handler.product_file),
	url(r'^products/generatecatalog/$', catalog_handler.product_catalog)
]

urlpatterns += [
	url(r'^ordershipment/$', order_handler.order_shipment_details),
	url(r'^orderitem/$', order_handler.order_item_details),
	url(r'^suborder/$', order_handler.suborder_details),
	url(r'^orders/$', order_handler.order_details),
	url(r'^buyerpayment/$', order_handler.buyer_payment_details),
	url(r'^sellerpayment/$', order_handler.seller_payment_details),
]

urlpatterns += [
	url(r'^users/$', user_handler.user_details)
]

urlpatterns += [
	url(r'^users/buyer/$', user_handler.buyer_details),
	url(r'^users/buyer/login/$', user_handler.buyer_login),
	url(r'^users/buyer/accesstoken/$', user_handler.buyer_access_token_details),
	url(r'^users/buyer/address/$', user_handler.buyer_address_details),
	url(r'^users/buyer/purchasingstate/$', user_handler.buyer_purchasing_state_details),
	url(r'^users/buyer/buysfrom/$', user_handler.buyer_buys_from_details),
	url(r'^users/buyer/buyerinterest/$', user_handler.buyer_interest_details),
	url(r'^users/buyer/buyerproducts/$', user_handler.buyer_product_details),
	url(r'^users/buyer/buyerproducts/whatsapp/$', user_handler.buyer_product_whatsapp_details),
	url(r'^users/buyer/buyerproducts/landing/$', user_handler.buyer_product_landing_details),
	url(r'^users/buyer/buyerproducts/masterupdate/$', user_handler.buyer_product_master_update),
	url(r'^users/buyer/buyersharedproductid/$', user_handler.buyer_shared_product_id_details),
	url(r'^users/buyer/buyerpanel/tracking/$', user_handler.buyer_panel_tracking_details),
]

urlpatterns += [
	url(r'^users/seller/$', user_handler.seller_details),
	url(r'^users/seller/login/$', user_handler.seller_login)
]

urlpatterns += [
	url(r'^users/businesstype/$', user_handler.business_type_details)
]

urlpatterns += [
	url(r'^users/internaluser/$', user_handler.internal_user_details),
	url(r'^users/internaluser/login/$', user_handler.internaluser_login)
]

urlpatterns += [
	url(r'^leads/buyer/$', lead_handler.buyer_leads),
	url(r'^leads/seller/$', lead_handler.seller_leads),
	url(r'^leads/contactus/$', lead_handler.contactus_leads)
]

urlpatterns += [
	url(r'^address/state/$', address_handler.state_details)
]

urlpatterns += [
	url(r'^blog/articles/$', blog_handler.article_details),
	url(r'^blog/articles/coverphoto/$', blog_handler.article_cover_photo_details),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
