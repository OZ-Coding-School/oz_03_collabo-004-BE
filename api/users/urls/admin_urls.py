from django.urls import path

from api.users.views.user_crud_views import (
    AdminArticleDetailView,
    AdminCommentDetailView,
    SwitchUserAuthorizationView,
    UserArticleCommentDeleteView,
    UserArticlesCommentsView,
    UserListForAdmin,
    UserRetrieveUpdateDeleteAdminView,
)

urlpatterns = [
    # 유저 권한 변경
    path(
        "state/<int:id>/",
        SwitchUserAuthorizationView.as_view(),
        name="change-user-role",
    ),
    path("users/", UserListForAdmin.as_view(), name="user-list"),
    path(
        "user/<int:id>/",
        UserRetrieveUpdateDeleteAdminView.as_view(),
        name="user-detail",
    ),
    path("article/<int:id>/", AdminArticleDetailView.as_view(), name="article-detail"),
    path("comment/<int:id>/", AdminCommentDetailView.as_view(), name="comment-detail"),
    path(
        "user/<int:id>/articles-comments/",
        UserArticlesCommentsView.as_view(),
        name="user-articles-comments",
    ),
    path(
        "user/<int:id>/articles-comments/delete/",
        UserArticleCommentDeleteView.as_view(),
        name="user-delete-articles-comments",
    ),
]
