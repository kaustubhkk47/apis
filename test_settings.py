from conf.dev import *
import logging

SECRET_KEY = "3472-7#08av*-3&w23fi*#gi^k%=pcahzbxiu(uwrr79qbrd#p"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'simple_test_db'
    }
}


STATIC_ROOT = "/home/kaustubh/Desktop/NewStartUp/Code/websiteProject/static"
STATIC_URL = '/static/'
STATICFILES_DIRS = ('/home/kaustubh/Desktop/NewStartUp/Code/websiteProject/static/static/',)


MEDIA_ROOT = "/home/kaustubh/Desktop/NewStartUp/Code/websiteProject/static/media"
MEDIA_URL = '/media/'


EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'


PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)


DEBUG = False
TEMPLATE_DEBUG = False


logging.disable(logging.CRITICAL)