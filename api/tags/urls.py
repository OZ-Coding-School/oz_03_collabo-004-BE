from django.urls import path
from .views import TagListView, TagQuestionListView

urlpatterns = [
    path('list/', TagListView.as_view(), name='tag-list'),
]