from ai_hunsoos.views import AiHunsooDetailView
from django.urls import path

urlpatterns = [
    path(
        "<int:article_id>/",
        AiHunsooDetailView.as_view(),
        name="ai-hunsoo-detail",
    ),
]
