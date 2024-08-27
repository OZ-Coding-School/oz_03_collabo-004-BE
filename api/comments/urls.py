from django.urls import path

from .views.comment_crud_views import (
    CommentCreateView,
    CommentDetailView,
    CommentListView,
    CommentUpdateView,
)
from .views.comment_reaction_views import CommentReactionToggleView, CommentSelectView

urlpatterns = [
    path(
        "create/articles/<int:article_id>/",
        CommentCreateView.as_view(),
        name="comment-create",
    ),
    path("edit/<int:pk>/", CommentUpdateView.as_view(), name="comment-update"),
    path(
        "list/articles/<int:article_id>/",
        CommentListView.as_view(),
        name="comment-list",
    ),
    path("<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
    path(
        "<int:pk>/react/",
        CommentReactionToggleView.as_view(),
        name="comment-reaction-toggle",
    ),
    path(
        "<int:pk>/select/",
        CommentSelectView.as_view(),
        name="comment-select",
    ),
]
