from django.urls import path
from .views import TagListView, TagQuestionListView

urlpatterns = [
    path('tags/', TagListView.as_view(), name='tag-list'),
]