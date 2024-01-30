from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path

urlpatterns = [
    path("", include("course.urls")),
    path("admin/", admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()
