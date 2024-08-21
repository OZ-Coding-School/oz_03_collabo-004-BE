from django.urls import path

from .views import TagListView

urlpatterns = [
    path("list/", TagListView.as_view(), name="tag-list"),
]
