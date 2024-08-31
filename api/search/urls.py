from django.urls import path

from .views import ArticleSearchView

urlpatterns = [
    path("", ArticleSearchView.as_view(), name="article-search"),
]
