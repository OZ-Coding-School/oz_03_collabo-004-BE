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
        "users/<int:id>/change-role/",
        SwitchUserAuthorizationView.as_view(),
        name="change-user-role",
    ),
    # 모든 유저 정보 조회
    path("users/", UserListForAdmin.as_view(), name="user-list"),
    # 특정 유저 정보 조회, 수정, 삭제
    path(
        "users/<int:id>/",
        UserRetrieveUpdateDeleteAdminView.as_view(),
        name="user-detail",
    ),
    # 특정 게시글 조회 및 삭제
    path("articles/<int:id>/", AdminArticleDetailView.as_view(), name="article-detail"),
    # 특정 댓글 조회 및 삭제
    path("comments/<int:id>/", AdminCommentDetailView.as_view(), name="comment-detail"),
    # 특정 사용자가 작성한 게시글과 댓글 조회
    path(
        "users/<int:id>/articles-comments/",
        UserArticlesCommentsView.as_view(),
        name="user-articles-comments",
    ),
    # 특정 사용자가 작성한 게시글과 댓글 삭제
    path(
        "users/<int:id>/delete-articles-comments/",
        UserArticleCommentDeleteView.as_view(),
        name="user-delete-articles-comments",
    ),
]
