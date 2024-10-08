"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", include("common.urls")),
    path("api/auth/", include("users.urls.auth_urls")),
    path("api/admin/", include("users.urls.admin_urls")),
    path("api/account/", include("profiles.urls")),
    path("api/tag/", include("tags.urls")),
    path("api/article/", include("articles.urls")),
    path("api/ai_hunsu/", include("ai_hunsoos.urls")),
    path("api/comment/", include("comments.urls")),
    path("api/notification/", include("notifications.urls")),
    path("api/report/", include("reports.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
