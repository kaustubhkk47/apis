from .base import *

WKHTMLTOPDFPATH = '/usr/local/bin/wkhtmltopdf'

DEBUG = False
ALLOWED_HOSTS = ["*"]

CURRENT_ENVIRONMENT = 'test'

BASE_URL = "http://beta.wholdus.com"
API_BASE_URL = "http://api-test.wholdus.com"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s [%(pathname)s func: %(funcName)s line: %(lineno)d] [Process %(processName)s Thread %(threadName)s] %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s [%(pathname)s func: %(funcName)s line: %(lineno)d] %(message)s'
        },
    },
    'handlers': {
        'file_warn': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': WARN_LOG_FILE_PATH,
            'formatter':'simple'
        },
        'file_critical': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': CRITICAL_LOG_FILE_PATH,
            'formatter':'simple'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter':'simple'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file_warn','file_critical'],
            'level': 'WARNING',
            'propagate': True,
        }
    }
}