from django.urls import path

from .views import ArticleReportCreateView, CommentReportCreateView

urlpatterns = [
    path(
        "article/<int:article_id>",
        ArticleReportCreateView.as_view(),
        name="article-report-create",
    ),
    path(
        "comment/<int:comment_id>",
        CommentReportCreateView.as_view(),
        name="comment-report-create",
    ),
]
