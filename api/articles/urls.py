from django.urls import path

from .views.article_crud_views import (
    ArticleCreateView,
    ArticleDeleteView,
    ArticleImageUploadView,
    ArticleUpdateView,
)
from .views.article_list_views import (
    ArticleByTagView,
    ArticleDetailView,
    ArticleListView,
)
from .views.article_reaction_views import (
    ArticleLikeToggleView,
    ArticleViewCountView,
    TopLikedArticlesView,
)
from .views.article_search_views import article_search_view

urlpatterns = [
    # CRUD 관련 URL
    path("create/", ArticleCreateView.as_view(), name="article-create"),
    path("delete/<int:id>/", ArticleDeleteView.as_view(), name="article-delete"),
    path("update/<int:id>/", ArticleUpdateView.as_view(), name="article-update"),
    path(
        "images/",
        ArticleImageUploadView.as_view(),
        name="article-image-upload",
    ),
    # 게시글 리스트 및 상세 조회 관련 URL
    path("", ArticleListView.as_view(), name="article-list"),
    path("<int:id>/", ArticleDetailView.as_view(), name="article-detail"),
    path("tag/<int:tag_id>/", ArticleByTagView.as_view(), name="articles-by-tag"),
    # 반응 (조회수, 좋아요) 관련 URL
    path("<int:id>/view/", ArticleViewCountView.as_view(), name="article-view-count"),
    path("<int:id>/like/", ArticleLikeToggleView.as_view(), name="article-like"),
    # 검색 관련 URL
    path("search/", article_search_view, name="article_search"),
    path(
        "top/",
        TopLikedArticlesView.as_view(),
        name="top-liked-articles",
    ),
]
