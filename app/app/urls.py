"""
URL configuration for nginx_logs project.

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

from django.contrib import admin
from django.urls import include, path

from nginx_logs.api.v1 import urls as api_v1_urls
from nginx_logs.views import main_page


urlpatterns = [
    path("api/v1/", include(api_v1_urls)),
    path("admin/", admin.site.urls),
    path("", main_page, name="main-page"),
]
