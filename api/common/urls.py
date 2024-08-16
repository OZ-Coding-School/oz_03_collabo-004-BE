from django.urls import path

from . import views

urlpatterns = [
    path("", views.HealthCheck.as_view()),
]
