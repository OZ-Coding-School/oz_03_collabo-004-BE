from django.contrib import admin

from .models import Article, ArticleImage

admin.site.register(Article)
admin.site.register(ArticleImage)
