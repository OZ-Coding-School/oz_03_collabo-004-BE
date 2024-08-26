from django.urls import path

from ..views.user_crud_views import (
    AdminArticleDetailView,
    AdminCommentDetailView,
    SwitchUserAuthorizationView,
    UserArticleCommentDeleteView,
    UserArticlesCommentsView,
    UserListForAdmin,
    UserRetrieveUpdateDeleteAdminView,
)

urlpatterns = [
    path(
        "state/<int:id>/",
        SwitchUserAuthorizationView.as_view(),
        name="change-user-role",
    ),
    path("users/", UserListForAdmin.as_view(), name="user-list-admin"),
    path(
        "user/<int:id>/",
        UserRetrieveUpdateDeleteAdminView.as_view(),
        name="user-detail-admin",
    ),
    path(
        "article/<int:id>/",
        AdminArticleDetailView.as_view(),
        name="article-detail-admin",
    ),
    path(
        "comment/<int:id>/",
        AdminCommentDetailView.as_view(),
        name="comment-detail-admin",
    ),
    path(
        "user/<int:id>/articles-comments/",
        UserArticlesCommentsView.as_view(),
        name="user-articles-comments-admin",
    ),
    path(
        "user/<int:id>/articles-comments/delete/",
        UserArticleCommentDeleteView.as_view(),
        name="user-delete-articles-comments-admin",
    ),
]
