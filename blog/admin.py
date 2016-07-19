from django.contrib import admin

from .models.article import *

admin.site.register(Article, ArticleAdmin)
